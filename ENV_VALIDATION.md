# Environment Variable Validation

## Overview

The AWS Cloud Engineer Agent now includes comprehensive environment variable validation at application startup. This ensures that all required AWS credentials and configuration are properly set before the application attempts to connect to AWS services.

## Required Environment Variables

The following environment variables **must** be set for the application to start:

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_REGION` | AWS region for Bedrock and other AWS services | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS access key ID for authentication | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key for authentication | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |

## Optional Environment Variables

The following environment variables are optional but may be required depending on your AWS authentication method:

| Variable | Description | When Required |
|----------|-------------|---------------|
| `AWS_SESSION_TOKEN` | AWS session token | Required when using temporary credentials (e.g., from AWS STS, IAM roles, or SSO) |

## Setting Environment Variables

### Linux/macOS

```bash
export AWS_REGION='us-east-1'
export AWS_ACCESS_KEY_ID='your-access-key-id'
export AWS_SECRET_ACCESS_KEY='your-secret-access-key'
# Optional: for temporary credentials
export AWS_SESSION_TOKEN='your-session-token'
```

### Windows PowerShell

```powershell
$env:AWS_REGION='us-east-1'
$env:AWS_ACCESS_KEY_ID='your-access-key-id'
$env:AWS_SECRET_ACCESS_KEY='your-secret-access-key'
# Optional: for temporary credentials
$env:AWS_SESSION_TOKEN='your-session-token'
```

### Windows Command Prompt

```cmd
set AWS_REGION=us-east-1
set AWS_ACCESS_KEY_ID=your-access-key-id
set AWS_SECRET_ACCESS_KEY=your-secret-access-key
REM Optional: for temporary credentials
set AWS_SESSION_TOKEN=your-session-token
```

### Using AWS CLI

You can configure your AWS credentials using the AWS CLI:

```bash
aws configure
```

This will set up your credentials in `~/.aws/credentials`, but you still need to set the `AWS_REGION` environment variable:

```bash
export AWS_REGION='us-east-1'  # Linux/macOS
$env:AWS_REGION='us-east-1'    # Windows PowerShell
```

### Using Docker

When running the application in Docker, pass environment variables using the `-e` flag:

```bash
docker run -d \
  -e AWS_REGION='us-east-1' \
  -e AWS_ACCESS_KEY_ID='your-access-key-id' \
  -e AWS_SECRET_ACCESS_KEY='your-secret-access-key' \
  -p 8501:8501 \
  cloudeng-strands-agent:latest
```

Or use an environment file:

```bash
# Create .env file
cat > .env << EOF
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
EOF

# Run with environment file
docker run -d --env-file .env -p 8501:8501 cloudeng-strands-agent:latest
```

## Validation Behavior

### Startup Validation

When the application starts:

1. **Environment variables are checked** before any AWS service connections are attempted
2. **Clear error messages** are displayed if required variables are missing
3. **The application will not start** if critical environment variables are not set
4. **Warnings are shown** for optional variables that may be needed for certain authentication methods

### Success Output

When all required variables are properly configured:

```
✓ Environment variable validation passed
  - AWS_REGION: us-east-1
  - AWS_ACCESS_KEY_ID: **************** (configured)
  - AWS_SECRET_ACCESS_KEY: **************** (configured)
```

### Error Output

If required variables are missing:

```
================================================================================
ERROR: Required AWS Environment Variables Missing
================================================================================

The following required environment variables are not set:

  ✗ AWS_REGION
    Purpose: AWS region for Bedrock and other AWS services

  ✗ AWS_ACCESS_KEY_ID
    Purpose: AWS access key ID for authentication

  ✗ AWS_SECRET_ACCESS_KEY
    Purpose: AWS secret access key for authentication

[... detailed instructions follow ...]
```

## Testing Validation

You can test the environment validation directly:

```bash
# Test with current environment
python3 env_validator.py

# Test with specific variables
AWS_REGION=us-east-1 \
AWS_ACCESS_KEY_ID=test \
AWS_SECRET_ACCESS_KEY=test \
python3 env_validator.py
```

Run the comprehensive test suite:

```bash
python3 test_env_validation.py
```

## Integration

The validation is automatically integrated into both application entry points:

1. **app.py** - Streamlit web interface validates before loading the agent
2. **cloud_engineer_agent.py** - Agent module validates before initializing AWS connections

This ensures that no matter how the application is started, environment variables are validated first.

## Security Best Practices

- **Never commit credentials** to version control
- **Use IAM roles** when running on EC2 or ECS (credentials are automatically provided)
- **Use temporary credentials** when possible (AWS SSO, STS assume-role)
- **Rotate credentials regularly** following AWS security best practices
- **Use AWS Secrets Manager or Parameter Store** for production deployments
- **Ensure .env files are in .gitignore** if using environment file loaders

## Troubleshooting

### Issue: Application exits immediately

**Cause**: Required environment variables are not set

**Solution**: Check the error message and set the missing variables as shown above

### Issue: Warning about AWS_SESSION_TOKEN

**Cause**: Session token is optional for long-term credentials but required for temporary credentials

**Solution**: If using temporary credentials (SSO, assumed roles), set the `AWS_SESSION_TOKEN` variable

### Issue: Credentials work with AWS CLI but not with the agent

**Cause**: AWS CLI may use profile-based credentials, while the agent requires environment variables

**Solution**: Either:
1. Set environment variables explicitly, or
2. Use `aws configure export-credentials` to get credentials and set as environment variables

### Issue: Running in containers

**Cause**: Container environments are isolated and don't inherit shell environment variables

**Solution**: Pass environment variables to the container using `-e` flags or `--env-file` option
