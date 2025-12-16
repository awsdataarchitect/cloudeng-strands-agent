# AWS Cloud Engineer Agent

This project demonstrates a powerful AWS Cloud Engineer Agent built with the [Strands Agents SDK](https://strandsagents.com/0.1.x/), showcasing how easily you can create sophisticated AI agents with a model-first approach. The agent can perform various cloud engineering tasks on AWS accounts, such as resource monitoring, security analysis, cost optimization, and more.

## Features

### Core Capabilities
- **AWS Resource Management**: Monitor, analyze, and manage AWS resources across multiple services
- **Security Analysis**: Identify security vulnerabilities and recommend best practices
- **Cost Optimization**: Find cost-saving opportunities and recommend resource optimizations
- **Infrastructure Diagramming**: Generate AWS architecture diagrams from text descriptions
- **AWS Documentation Search**: Find relevant AWS documentation for any service or feature
- **Direct AWS API Access**: Execute AWS CLI commands through the agent interface

### Predefined Tasks
- EC2 instance status monitoring
- S3 bucket analysis and management
- CloudWatch alarm status checking
- IAM user activity tracking
- Security group vulnerability analysis
- Cost optimization recommendations
- Lambda function management
- RDS instance monitoring
- VPC configuration analysis
- EBS volume optimization
- AWS architecture diagram generation

### Technical Features
- **Strands Agents SDK Integration**: Leverages the Strands framework for agent capabilities with its model-first approach
- **AWS Bedrock Integration**: Uses Amazon Nova Premier model (`us.amazon.nova-premier-v1`) for AI capabilities
- **MCP Tools Integration**: Incorporates AWS Documentation and AWS Diagram MCP tools
- **AWS CLI Integration**: Direct access to AWS API through the `use_aws` tool
- **Streamlit UI**: User-friendly interface for interacting with the agent
- **Health Check Endpoints**: Built-in monitoring endpoints for container orchestration and health monitoring
- **Containerized Deployment**: Docker-based deployment for portability
- **CDK Infrastructure**: Infrastructure as Code using AWS CDK TypeScript

## Architecture

The solution consists of:

1. **Strands Agent**: Built using the Strands Agents SDK with AWS Bedrock Amazon Nova Premier model (`us.amazon.nova-premier-v1`), implementing the agentic loop architecture
2. **Streamlit UI**: User-friendly interface for interacting with the agent
3. **AWS Infrastructure**: Deployed using CDK with:
   - ECR repository for the Docker image
   - ECS Fargate service for running the agent
   - Application Load Balancer for routing traffic
   - Public subnet configuration (no NAT Gateway)
   - Automated ECR deployment using cdk-ecr-deployment

### Architecture Diagram

![AWS Cloud Engineer Agent Architecture](./aws_cloud_engineer_agent_architecture.png)

## Local Development

### Prerequisites

- Python 3.11+
- AWS CLI configured with appropriate permissions
- Node.js and npm (for CDK)
- AWS Bedrock access with permissions for Amazon Nova Premier model

### Setup

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the Streamlit app locally:
   ```
   streamlit run app.py
   ```

### Health Check Endpoints

The application includes built-in health check endpoints for monitoring and container orchestration:

#### Available Endpoints

1. **Main Health Check** (`/health`)
   - **URL**: `http://localhost:8080/health`
   - **Purpose**: Comprehensive health check including environment variables, dependencies, and application files
   - **Returns**: 
     - HTTP 200: Application is healthy or degraded (with warnings)
     - HTTP 503: Application is unhealthy (critical issues detected)
   - **Response Format**:
     ```json
     {
       "status": "healthy|degraded|unhealthy",
       "timestamp": "2025-12-16T15:00:00Z",
       "application": "cloudeng-strands-agent",
       "checks": {
         "environment": {"status": "ok", "message": "..."},
         "dependencies": {"status": "ok", "message": "..."},
         "files": {"status": "ok", "message": "..."}
       }
     }
     ```

2. **Liveness Probe** (`/health/live`)
   - **URL**: `http://localhost:8080/health/live`
   - **Purpose**: Simple check to verify the server is responding
   - **Returns**: HTTP 200 if server is alive
   - **Use Case**: Kubernetes liveness probe, Docker health check

3. **Readiness Probe** (`/health/ready`)
   - **URL**: `http://localhost:8080/health/ready`
   - **Purpose**: Checks if the application is ready to accept traffic
   - **Returns**: 
     - HTTP 200: Ready to accept requests
     - HTTP 503: Not ready (missing dependencies or configuration)
   - **Use Case**: Kubernetes readiness probe, load balancer health check

#### Testing Health Checks

Run the health check test script:
```bash
# Test locally (default: http://localhost:8080)
python test_health_check.py

# Test against a specific URL
python test_health_check.py http://your-server:8080
```

Or test manually with curl:
```bash
# Main health check
curl http://localhost:8080/health

# Liveness probe
curl http://localhost:8080/health/live

# Readiness probe
curl http://localhost:8080/health/ready
```

#### Docker Health Check

When running in Docker, the health check server runs on port 8080:
```bash
# Build the image
docker build -t cloudeng-strands-agent .

# Run with health check port exposed
docker run -p 8501:8501 -p 8080:8080 \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  cloudeng-strands-agent

# Check health status
curl http://localhost:8080/health
```

#### Integration with Monitoring Systems

The health check endpoints can be integrated with:
- **Kubernetes**: Configure liveness and readiness probes
- **AWS ECS**: Use the health check for target group health checks
- **Docker Compose**: Define healthcheck in docker-compose.yml
- **Monitoring Tools**: Prometheus, Datadog, New Relic, etc.

Example Kubernetes configuration:
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
```

### Windows Compatibility

When running on Windows systems, the application automatically uses a Windows-compatible configuration for the MCP servers. The code detects the platform and adjusts accordingly.

#### Setup for Windows

1. Ensure you have Python 3.11+ installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Make sure the `uv` package is installed:
   ```
   pip install uv
   ```
4. Configure your AWS credentials properly

#### Running on Windows

You can run the application in two ways:

1. **Recommended: Using Streamlit**
   ```
   streamlit run app.py
   ```

2. **Direct execution** (if you want to run cloud_engineer_agent.py directly)
   ```
   python cloud_engineer_agent.py
   ```

#### Windows Configuration

The application uses the following configuration for Windows:
```json
{
  "mcpServers": {
    "aws-docs": {
      "command": "uv",
      "args": [
        "tool",
        "run",
        "--from",
        "awslabs.aws-documentation-mcp-server@latest",
        "awslabs.aws-documentation-mcp-server.exe"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      }
    }
  }
}
```

#### Troubleshooting Windows Issues

If you encounter errors when running the application on Windows:

1. **Verify Dependencies**:
   - Ensure you have Python 3.11+ installed
   - Confirm that you've installed all dependencies: `pip install -r requirements.txt`
   - Make sure the `uv` package is installed: `pip install uv`

2. **Check Permissions**:
   - Try running the command prompt or PowerShell as Administrator
   - Ensure your user has permissions to execute Python scripts

3. **Network Issues**:
   - Check your firewall settings to ensure Python has network access
   - Verify your internet connection is working properly

4. **Common Error Messages**:
   - "Connection closed": This typically indicates a problem with the MCP server initialization
   - "Command not found": Ensure the `uv` package is installed correctly

5. **Alternative Approach**:
   - If direct execution fails, try using Streamlit: `streamlit run app.py`

## Deployment

### Prerequisites

- AWS CDK installed and bootstrapped
- Docker installed locally
- AWS account with Bedrock access enabled

### Deploy to AWS

1. Navigate to the CDK directory:
   ```
   cd cloud-engineer-agent-cdk
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Build the TypeScript code:
   ```
   npm run build
   ```

4. Deploy the stack:
   ```
   cdk deploy
   ```

5. Access the agent using the URL provided in the CDK output.

## Environment Variables

The following environment variables are used:

- `AWS_REGION`: AWS region for API calls (must be a region where Amazon Nova Premier is available)
- `AWS_ACCESS_KEY_ID`: AWS access key (for local development)
- `AWS_SECRET_ACCESS_KEY`: AWS secret key (for local development)

## Security Considerations

- The agent uses IAM roles with least privilege
- Bedrock permissions are scoped to necessary model invocation actions
- All communications use HTTPS
- Sensitive information is not stored in the application

## Strands Agents SDK

This project leverages the [Strands Agents SDK](https://strandsagents.com/0.1.x/), a powerful framework for building AI agents with a model-first approach. Key features include:

### Model-First Approach
Strands Agents SDK uses a model-first approach where the LLM acts as the orchestrator, making decisions about which tools to use and when. This approach allows for more flexible and intelligent agents that can adapt to complex scenarios.

### Agentic Loop Architecture
The SDK implements an agentic loop architecture where:
1. The agent receives a user request
2. The LLM analyzes the request and determines the best course of action
3. The agent executes tools as directed by the LLM
4. Results are fed back to the LLM for further analysis
5. The process repeats until the task is complete

This architecture enables sophisticated reasoning and multi-step problem solving without hardcoded workflows.

### MCP Integration
This project utilizes two Model Context Protocol (MCP) servers:
- **AWS Documentation MCP Server**: Provides access to comprehensive AWS documentation, allowing the agent to retrieve accurate information about AWS services, features, and best practices.
- **AWS Diagram MCP Server**: Enables the agent to generate visual AWS architecture diagrams based on text descriptions.

### Benefits
- **Simplified Development**: Create powerful agents with minimal code
- **Flexible Tool Integration**: Easily add new tools and capabilities
- **Intelligent Decision Making**: Let the LLM decide the best approach to solving problems
- **Transparent Reasoning**: Follow the agent's thought process and tool usage
- **Extensible Framework**: Build on top of the core architecture for specialized use cases
- **Built-in MCP**: Native support for Model Context Protocol (MCP) servers, enabling access to thousands of pre-built tools

### Documentation
For more information about Strands Agents SDK, visit the [official documentation](https://strandsagents.com/0.1.x/).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
