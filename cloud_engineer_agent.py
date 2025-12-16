from strands import Agent
from strands.tools.mcp import MCPClient
from strands.models import BedrockModel
from mcp import StdioServerParameters, stdio_client
from strands_tools import use_aws

import os
import sys
import atexit
from typing import Dict

# Import environment validation
from env_validator import validate_environment_variables, EnvironmentValidationError

# Validate environment variables at module initialization
print("Validating AWS environment variables...")
try:
    validate_environment_variables()
except EnvironmentValidationError as e:
    print(str(e), file=sys.stderr)
    print("\nFATAL: Cannot start application without required AWS credentials.", file=sys.stderr)
    sys.exit(1)

# Define common cloud engineering tasks
PREDEFINED_TASKS = {
    "ec2_status": "List all EC2 instances and their status",
    "s3_buckets": "List all S3 buckets and their creation dates",
    "cloudwatch_alarms": "Check for any CloudWatch alarms in ALARM state",
    "iam_users": "List all IAM users and their last activity",
    "security_groups": "Analyze security groups for potential vulnerabilities",
    "cost_optimization": "Identify resources that could be optimized for cost",
    "lambda_functions": "List all Lambda functions and their runtime",
    "rds_instances": "Check status of all RDS instances",
    "vpc_analysis": "Analyze VPC configuration and suggest improvements",
    "ebs_volumes": "Find unattached EBS volumes that could be removed",
    "generate_diagram": "Generate AWS architecture diagrams based on user description"
}

# Set up MCP clients with platform-specific configurations
is_windows = sys.platform.startswith('win')
print(f"Detected platform: {'Windows' if is_windows else 'Non-Windows (Linux/macOS)'}")

# Track whether MCP clients were successfully initialized
mcp_initialized = False
aws_docs_mcp_client = None
aws_diagram_mcp_client = None

def initialize_mcp_client(client_name, client_factory):
    """
    Safely initialize a single MCP client with proper error handling.
    Returns (client, success) tuple.
    """
    try:
        print(f"Initializing {client_name}...")
        client = client_factory()
        print(f"Starting {client_name}...")
        client.start()
        print(f"{client_name} started successfully.")
        return client, True
    except BaseException as e:
        # Catch BaseException to handle both Exception and ExceptionGroup (from TaskGroup)
        error_type = type(e).__name__
        error_message = str(e)
        
        # Handle ExceptionGroup specially (Python 3.11+ async TaskGroup errors)
        if error_type == "ExceptionGroup":
            print(f"Error initializing {client_name}: TaskGroup exception occurred")
            print(f"  Exception type: {error_type}")
            # Extract sub-exceptions from ExceptionGroup
            if hasattr(e, 'exceptions'):
                print(f"  Sub-exceptions ({len(e.exceptions)}):")
                for i, sub_exc in enumerate(e.exceptions, 1):
                    print(f"    {i}. {type(sub_exc).__name__}: {sub_exc}")
            else:
                print(f"  Details: {error_message}")
        else:
            print(f"Error initializing {client_name}: {error_message}")
        
        return None, False

try:
    if is_windows:
        # Windows-specific configuration
        print("Using Windows-specific MCP configuration...")
        
        # Try to initialize AWS Documentation MCP client
        aws_docs_mcp_client, docs_success = initialize_mcp_client(
            "AWS Documentation MCP client",
            lambda: MCPClient(lambda: stdio_client(
                StdioServerParameters(
                    command="uv",
                    args=["tool", "run", "--from", "awslabs.aws-documentation-mcp-server@latest", "awslabs.aws-documentation-mcp-server.exe"],
                    env={"FASTMCP_LOG_LEVEL": "ERROR"}
                )
            ))
        )
        
        # Try to initialize AWS Diagram MCP client
        aws_diagram_mcp_client, diagram_success = initialize_mcp_client(
            "AWS Diagram MCP client",
            lambda: MCPClient(lambda: stdio_client(
                StdioServerParameters(
                    command="uv",
                    args=["tool", "run", "--from", "awslabs.aws-diagram-mcp-server@latest", "awslabs.aws-diagram-mcp-server.exe"],
                    env={"FASTMCP_LOG_LEVEL": "ERROR"}
                )
            ))
        )
    else:
        # Non-Windows configuration (Linux/macOS)
        print("Using standard MCP configuration for Linux/macOS...")
        
        # Try to initialize AWS Documentation MCP client
        aws_docs_mcp_client, docs_success = initialize_mcp_client(
            "AWS Documentation MCP client",
            lambda: MCPClient(lambda: stdio_client(
                StdioServerParameters(command="uvx", args=["awslabs.aws-documentation-mcp-server@latest"])
            ))
        )
        
        # Try to initialize AWS Diagram MCP client
        aws_diagram_mcp_client, diagram_success = initialize_mcp_client(
            "AWS Diagram MCP client",
            lambda: MCPClient(lambda: stdio_client(
                StdioServerParameters(command="uvx", args=["awslabs.aws-diagram-mcp-server@latest"])
            ))
        )
    
    # Mark MCP as successfully initialized if at least one client started
    mcp_initialized = (aws_docs_mcp_client is not None or aws_diagram_mcp_client is not None)
    
    if not mcp_initialized:
        raise RuntimeError("Failed to initialize any MCP clients")
    
    print(f"\nMCP initialization complete. Active clients: " +
          f"Documentation={'Yes' if aws_docs_mcp_client else 'No'}, " +
          f"Diagram={'Yes' if aws_diagram_mcp_client else 'No'}")
    
except BaseException as e:
    # Catch any remaining exceptions including ExceptionGroup
    error_type = type(e).__name__
    error_message = str(e)
    
    print(f"\nMCP client initialization failed ({error_type}): {error_message}")
    
    if is_windows:
        print("\nWindows-specific troubleshooting tips:")
        print("1. Ensure you have installed the 'uv' package: pip install uv")
        print("2. Check if you have proper permissions to execute the commands")
        print("3. Verify your network connection and firewall settings")
        print("4. Try running the application with administrator privileges")
        print("5. If the issue persists, try running the Streamlit app instead: streamlit run app.py")
    else:
        print("\nTroubleshooting tips:")
        print("1. Ensure you have installed all dependencies: pip install -r requirements.txt")
        print("2. Check your network connection")
        print("3. Try running the Streamlit app instead: streamlit run app.py")
    
    # Ensure graceful degradation - clean up any partially initialized clients
    if aws_docs_mcp_client is not None:
        try:
            aws_docs_mcp_client.stop()
        except:
            pass
    if aws_diagram_mcp_client is not None:
        try:
            aws_diagram_mcp_client.stop()
        except:
            pass
    
    # Reset to None for clean state
    aws_docs_mcp_client = None
    aws_diagram_mcp_client = None
    mcp_initialized = False
    
    # Continue with limited functionality instead of crashing
    print("\nContinuing with limited functionality (MCP tools disabled)...")

# Get tools from MCP clients (if initialized)
docs_tools = aws_docs_mcp_client.list_tools_sync() if mcp_initialized and aws_docs_mcp_client is not None else []
diagram_tools = aws_diagram_mcp_client.list_tools_sync() if mcp_initialized and aws_diagram_mcp_client is not None else []

# Create a BedrockModel with system inference profile
bedrock_model = BedrockModel(
    model_id="us.amazon.nova-premier-v1:0",  # System inference profile ID
    region_name=os.environ.get("AWS_REGION", "us-east-1"),
    temperature=0.1,
)

# System prompt for the agent
system_prompt = """
You are an expert AWS Cloud Engineer assistant. Your job is to help with AWS infrastructure 
management, optimization, security, and best practices. You can:

1. Analyze AWS resources and configurations
2. Provide recommendations for security improvements
3. Identify cost optimization opportunities
4. Troubleshoot AWS service issues
5. Explain AWS concepts and best practices
6. Generate infrastructure diagrams using the AWS diagram tools
7. Search AWS documentation for specific information

When asked to create diagrams, use the AWS diagram MCP tools to generate visual representations
of architecture based on the user's description. Be creative and thorough in translating text
descriptions into complete architecture diagrams.

Always provide clear, actionable advice with specific AWS CLI commands or console steps when applicable.
Focus on security best practices and cost optimization in your recommendations.

IMPORTANT: Never include <thinking> tags or expose your internal thought process in responses.
"""

# Create the agent with all tools and Bedrock Nova Premier model
agent = Agent(
    tools=[use_aws] + docs_tools + diagram_tools,
    model=bedrock_model,
    system_prompt=system_prompt
)

# Register cleanup handler for MCP clients
def cleanup():
    if mcp_initialized and aws_docs_mcp_client is not None:
        try:
            aws_docs_mcp_client.stop()
            print("AWS Documentation MCP client stopped")
        except Exception as e:
            print(f"Error stopping AWS Documentation MCP client: {e}")
    
    if mcp_initialized and aws_diagram_mcp_client is not None:
        try:
            aws_diagram_mcp_client.stop()
            print("AWS Diagram MCP client stopped")
        except Exception as e:
            print(f"Error stopping AWS Diagram MCP client: {e}")

atexit.register(cleanup)

# Function to execute a predefined task
def execute_predefined_task(task_key: str) -> str:
    """Execute a predefined cloud engineering task"""
    if task_key not in PREDEFINED_TASKS:
        return f"Error: Task '{task_key}' not found in predefined tasks."
    
    task_description = PREDEFINED_TASKS[task_key]
    return execute_custom_task(task_description)

# Function to execute a custom task
def execute_custom_task(task_description: str) -> str:
    """Execute a custom cloud engineering task based on description"""
    try:
        response = agent(task_description)
        
        # Handle AgentResult object by extracting the message
        if hasattr(response, 'message'):
            return response.message
        
        # Handle other types of responses
        return str(response)
    except Exception as e:
        return f"Error executing task: {str(e)}"

# Function to get predefined tasks
def get_predefined_tasks() -> Dict[str, str]:
    """Return the dictionary of predefined tasks"""
    return PREDEFINED_TASKS


if __name__ == "__main__":
    # Example usage
    result = execute_custom_task("List all EC2 instances and their status")
    print(result)
