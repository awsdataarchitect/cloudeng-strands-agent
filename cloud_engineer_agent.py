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

try:
    if is_windows:
        # Windows-specific configuration
        print("Using Windows-specific MCP configuration...")
        # Set up AWS Documentation MCP client for Windows
        aws_docs_mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="uv",
                args=["tool", "run", "--from", "awslabs.aws-documentation-mcp-server@latest", "awslabs.aws-documentation-mcp-server.exe"],
                env={"FASTMCP_LOG_LEVEL": "ERROR"}
            )
        ))
        
        # Set up AWS Diagram MCP client for Windows
        aws_diagram_mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="uv",
                args=["tool", "run", "--from", "awslabs.aws-diagram-mcp-server@latest", "awslabs.aws-diagram-mcp-server.exe"],
                env={"FASTMCP_LOG_LEVEL": "ERROR"}
            )
        ))
    else:
        # Non-Windows configuration (Linux/macOS)
        print("Using standard MCP configuration for Linux/macOS...")
        # Set up AWS Documentation MCP client
        aws_docs_mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(command="uvx", args=["awslabs.aws-documentation-mcp-server@latest"])
        ))
        
        # Set up AWS Diagram MCP client
        aws_diagram_mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(command="uvx", args=["awslabs.aws-diagram-mcp-server@latest"])
        ))

    # Start both MCP clients
    print("Starting AWS Documentation MCP client...")
    aws_docs_mcp_client.start()
    print("AWS Documentation MCP client started successfully.")
    
    print("Starting AWS Diagram MCP client...")
    aws_diagram_mcp_client.start()
    print("AWS Diagram MCP client started successfully.")
    
    # Mark MCP as successfully initialized
    mcp_initialized = True
    
except Exception as e:
    error_message = str(e)
    print(f"Error initializing MCP clients: {error_message}")
    
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
    
    # Continue with limited functionality instead of raising exception
    # This allows the module to be imported even if MCP initialization fails
    print("\nContinuing with limited functionality (MCP tools disabled)...")
    aws_docs_mcp_client = None
    aws_diagram_mcp_client = None

# Get tools from MCP clients (if initialized)
docs_tools = aws_docs_mcp_client.list_tools_sync() if mcp_initialized else []
diagram_tools = aws_diagram_mcp_client.list_tools_sync() if mcp_initialized else []

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
    if mcp_initialized:
        try:
            aws_docs_mcp_client.stop()
            print("AWS Documentation MCP client stopped")
        except Exception as e:
            print(f"Error stopping AWS Documentation MCP client: {e}")
    
    if mcp_initialized:
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
