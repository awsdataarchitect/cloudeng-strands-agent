#!/bin/bash

echo "========================================================================"
echo "AWS Cloud Engineer Agent - Environment Validation Demo"
echo "========================================================================"
echo ""

echo "Demo 1: Testing with MISSING environment variables"
echo "--------------------------------------------------------------------"
# Clear AWS environment variables
unset AWS_REGION AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
python3 env_validator.py
echo ""
echo "Result: Validation failed as expected (exit code: $?)"
echo ""

echo "========================================================================"
echo ""

echo "Demo 2: Testing with ALL required environment variables"
echo "--------------------------------------------------------------------"
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
python3 env_validator.py
echo ""
echo "Result: Validation passed (exit code: $?)"
echo ""

echo "========================================================================"
echo ""

echo "Demo 3: Testing with required + optional environment variables"
echo "--------------------------------------------------------------------"
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_SESSION_TOKEN=FwoGZXIvYXdzEBExample
python3 env_validator.py
echo ""
echo "Result: Validation passed with all variables (exit code: $?)"
echo ""

echo "========================================================================"
echo "Demo Complete!"
echo "========================================================================"
