from strands import Agent
from strands.tools.mcp import MCPClient
from strands.models import BedrockModel
from mcp import StdioServerParameters, stdio_client
from strands_tools import use_aws

import os
import sys
import atexit
import platform
import subprocess
from typing import Dict, List, Optional

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

# Check if uvx is installed
def is_uvx_installed():
    try:
        if platform.system() == "Windows":
            # On Windows, use where command
            subprocess.run(["where", "uvx"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            # On Unix-like systems, use which command
            subprocess.run(["which", "uvx"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

# Initialize MCP clients with error handling
aws_docs_mcp_client = None
aws_diagram_mcp_client = None
docs_tools = []
diagram_tools = []

def initialize_mcp_clients():
    global aws_docs_mcp_client, aws_diagram_mcp_client, docs_tools, diagram_tools
    
    if not is_uvx_installed():
        print("WARNING: 'uvx' command not found. MCP clients will not be available.")
        print("To use MCP clients, please install Universal Command Line Interface (uvx).")
        print("Visit: https://strandsagents.com/0.1.x/getting-started/installation/")
        return False
    
    try:
        # Set up AWS Documentation MCP client
        aws_docs_mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(command="uvx", args=["awslabs.aws-documentation-mcp-server@latest"])
        ))
        aws_docs_mcp_client.start()
        
        # Set up AWS Diagram MCP client
        aws_diagram_mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(command="uvx", args=["awslabs.aws-diagram-mcp-server@latest"])
        ))
        aws_diagram_mcp_client.start()
        
        # Get tools from MCP clients
        docs_tools = aws_docs_mcp_client.list_tools_sync()
        diagram_tools = aws_diagram_mcp_client.list_tools_sync()
        
        # Register cleanup handler for MCP clients
        atexit.register(cleanup)
        
        return True
    except Exception as e:
        print(f"ERROR: Failed to initialize MCP clients: {e}")
        print("The agent will continue with limited functionality (no AWS documentation or diagram tools).")
        return False

# Register cleanup handler for MCP clients
def cleanup():
    if aws_docs_mcp_client:
        try:
            aws_docs_mcp_client.stop()
            print("AWS Documentation MCP client stopped")
        except Exception as e:
            print(f"Error stopping AWS Documentation MCP client: {e}")
    
    if aws_diagram_mcp_client:
        try:
            aws_diagram_mcp_client.stop()
            print("AWS Diagram MCP client stopped")
        except Exception as e:
            print(f"Error stopping AWS Diagram MCP client: {e}")

# Initialize MCP clients
mcp_initialized = initialize_mcp_clients()

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
"""

# Add MCP-specific capabilities if available
if mcp_initialized:
    system_prompt += """
6. Generate infrastructure diagrams using the AWS diagram tools
7. Search AWS documentation for specific information

When asked to create diagrams, use the AWS diagram MCP tools to generate visual representations
of architecture based on the user's description. Be creative and thorough in translating text
descriptions into complete architecture diagrams.
"""

system_prompt += """
Always provide clear, actionable advice with specific AWS CLI commands or console steps when applicable.
Focus on security best practices and cost optimization in your recommendations.

IMPORTANT: Never include <thinking> tags or expose your internal thought process in responses.
"""

# Create the agent with available tools and Bedrock Nova Premier model
tools = [use_aws]
if mcp_initialized:
    tools.extend(docs_tools + diagram_tools)

# Create the agent with all tools and Bedrock Nova Premier model
agent = Agent(
    tools=tools,
    model=bedrock_model,
    system_prompt=system_prompt
)

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
    # Print status information
    print("\n=== AWS Cloud Engineer Agent ===\n")
    
    if not mcp_initialized:
        print("\nWARNING: Running with limited functionality (no AWS documentation or diagram tools).")
        print("To enable full functionality, please install the Universal Command Line Interface (uvx).")
        print("Visit: https://strandsagents.com/0.1.x/getting-started/installation/")
        print("\nYou can still use the agent for basic AWS operations.\n")
    else:
        print("All tools initialized successfully.\n")
    
    # Print available tasks
    print("Available predefined tasks:")
    for key, description in PREDEFINED_TASKS.items():
        print(f"  - {key}: {description}")
    
    print("\nRunning example task: 'List all EC2 instances and their status'")
    print("-" * 50)
    
    try:
        # Example usage
        result = execute_custom_task("List all EC2 instances and their status")
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Ensure you have valid AWS credentials configured")
        print("2. Check your internet connection")
        print("3. Verify that you have the required permissions in your AWS account")
        print("4. For full functionality, install uvx: https://strandsagents.com/0.1.x/getting-started/installation/")
        print("\nFor a better experience, try running the Streamlit app instead:")
        print("streamlit run app.py")
