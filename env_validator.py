"""
Environment variable validation module for AWS Cloud Engineer Agent.
Validates required AWS-related environment variables at application startup.
"""

import os
import sys
from typing import List, Tuple


class EnvironmentValidationError(Exception):
    """Custom exception for environment validation failures."""
    pass


def validate_environment_variables() -> None:
    """
    Validate required AWS environment variables at application startup.
    
    Raises:
        EnvironmentValidationError: If any required environment variables are missing.
    """
    required_vars = [
        ("AWS_REGION", "AWS region for Bedrock and other AWS services"),
        ("AWS_ACCESS_KEY_ID", "AWS access key ID for authentication"),
        ("AWS_SECRET_ACCESS_KEY", "AWS secret access key for authentication"),
    ]
    
    optional_vars = [
        ("AWS_SESSION_TOKEN", "AWS session token (required for temporary credentials)"),
    ]
    
    missing_required: List[Tuple[str, str]] = []
    missing_optional: List[Tuple[str, str]] = []
    
    # Check required variables
    for var_name, description in required_vars:
        value = os.environ.get(var_name)
        if not value or value.strip() == "":
            missing_required.append((var_name, description))
    
    # Check optional variables (for warnings)
    for var_name, description in optional_vars:
        value = os.environ.get(var_name)
        if not value or value.strip() == "":
            missing_optional.append((var_name, description))
    
    # If there are missing required variables, raise an error
    if missing_required:
        error_message = _format_error_message(missing_required, missing_optional)
        raise EnvironmentValidationError(error_message)
    
    # If there are missing optional variables, print warnings
    if missing_optional:
        _print_warnings(missing_optional)
    
    # Print success message
    print("✓ Environment variable validation passed")
    print(f"  - AWS_REGION: {os.environ.get('AWS_REGION')}")
    print(f"  - AWS_ACCESS_KEY_ID: {'*' * 16} (configured)")
    print(f"  - AWS_SECRET_ACCESS_KEY: {'*' * 16} (configured)")
    if os.environ.get("AWS_SESSION_TOKEN"):
        print(f"  - AWS_SESSION_TOKEN: {'*' * 16} (configured)")


def _format_error_message(
    missing_required: List[Tuple[str, str]], 
    missing_optional: List[Tuple[str, str]]
) -> str:
    """
    Format a detailed error message for missing environment variables.
    
    Args:
        missing_required: List of (variable_name, description) tuples for required variables
        missing_optional: List of (variable_name, description) tuples for optional variables
    
    Returns:
        Formatted error message string
    """
    lines = [
        "\n" + "=" * 80,
        "ERROR: Required AWS Environment Variables Missing",
        "=" * 80,
        "",
        "The following required environment variables are not set:",
        ""
    ]
    
    for var_name, description in missing_required:
        lines.append(f"  ✗ {var_name}")
        lines.append(f"    Purpose: {description}")
        lines.append("")
    
    lines.extend([
        "To fix this issue, please set the required environment variables:",
        "",
        "Option 1: Export in your shell (Linux/macOS):",
        "  export AWS_REGION='us-east-1'",
        "  export AWS_ACCESS_KEY_ID='your-access-key-id'",
        "  export AWS_SECRET_ACCESS_KEY='your-secret-access-key'",
        "",
        "Option 2: Set in your shell (Windows PowerShell):",
        "  $env:AWS_REGION='us-east-1'",
        "  $env:AWS_ACCESS_KEY_ID='your-access-key-id'",
        "  $env:AWS_SECRET_ACCESS_KEY='your-secret-access-key'",
        "",
        "Option 3: Create a .env file and use a tool to load it",
        "",
        "Option 4: Use AWS CLI to configure credentials:",
        "  aws configure",
        "  Then set AWS_REGION environment variable",
        "",
    ])
    
    if missing_optional:
        lines.extend([
            "Note: The following optional variables are also missing:",
            ""
        ])
        for var_name, description in missing_optional:
            lines.append(f"  ⚠ {var_name}")
            lines.append(f"    Purpose: {description}")
            lines.append("")
    
    lines.extend([
        "=" * 80,
        ""
    ])
    
    return "\n".join(lines)


def _print_warnings(missing_optional: List[Tuple[str, str]]) -> None:
    """
    Print warnings for missing optional environment variables.
    
    Args:
        missing_optional: List of (variable_name, description) tuples for optional variables
    """
    print("\n" + "-" * 80)
    print("WARNING: Optional AWS Environment Variables Missing")
    print("-" * 80)
    
    for var_name, description in missing_optional:
        print(f"  ⚠ {var_name}")
        print(f"    Purpose: {description}")
    
    print("\nThe application will continue, but some features may not work correctly")
    print("if you're using temporary credentials (e.g., from AWS STS).")
    print("-" * 80 + "\n")


if __name__ == "__main__":
    """Allow running this module directly for testing."""
    try:
        validate_environment_variables()
        print("\n✓ All required environment variables are properly configured!")
        sys.exit(0)
    except EnvironmentValidationError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
