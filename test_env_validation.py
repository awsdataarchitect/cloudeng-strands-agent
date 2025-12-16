#!/usr/bin/env python3
"""
Test script to verify environment variable validation.
This script tests both success and failure scenarios.
"""

import os
import sys
import subprocess

def run_validation_test(test_name, env_vars, expected_success):
    """Run a single validation test with specific environment variables."""
    print(f"\n{'='*80}")
    print(f"Test: {test_name}")
    print(f"{'='*80}")
    
    # Create a clean environment with only the test variables
    test_env = os.environ.copy()
    
    # Remove AWS variables to start fresh
    for key in list(test_env.keys()):
        if key.startswith('AWS_'):
            del test_env[key]
    
    # Add test-specific variables
    for key, value in env_vars.items():
        test_env[key] = value
        print(f"Setting {key}={value if key != 'AWS_SECRET_ACCESS_KEY' else '***'}")
    
    # Run the validation module
    result = subprocess.run(
        [sys.executable, 'env_validator.py'],
        env=test_env,
        capture_output=True,
        text=True,
        cwd='/projects/sandbox/cloudeng-strands-agent'
    )
    
    success = result.returncode == 0
    
    if success == expected_success:
        print(f"\n✓ Test PASSED (expected {'success' if expected_success else 'failure'})")
    else:
        print(f"\n✗ Test FAILED (expected {'success' if expected_success else 'failure'}, got {'success' if success else 'failure'})")
    
    print(f"\nStdout:\n{result.stdout}")
    if result.stderr:
        print(f"\nStderr:\n{result.stderr}")
    
    return success == expected_success

def main():
    """Run all validation tests."""
    print("Starting Environment Variable Validation Tests")
    print("="*80)
    
    all_tests_passed = True
    
    # Test 1: All required variables present
    all_tests_passed &= run_validation_test(
        "All Required Variables Present",
        {
            'AWS_REGION': 'us-east-1',
            'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
            'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
        },
        expected_success=True
    )
    
    # Test 2: All variables including optional
    all_tests_passed &= run_validation_test(
        "All Variables Including Optional",
        {
            'AWS_REGION': 'us-west-2',
            'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
            'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            'AWS_SESSION_TOKEN': 'FwoGZXIvYXdzEBExample'
        },
        expected_success=True
    )
    
    # Test 3: Missing AWS_REGION
    all_tests_passed &= run_validation_test(
        "Missing AWS_REGION",
        {
            'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
            'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
        },
        expected_success=False
    )
    
    # Test 4: Missing AWS_ACCESS_KEY_ID
    all_tests_passed &= run_validation_test(
        "Missing AWS_ACCESS_KEY_ID",
        {
            'AWS_REGION': 'us-east-1',
            'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
        },
        expected_success=False
    )
    
    # Test 5: Missing AWS_SECRET_ACCESS_KEY
    all_tests_passed &= run_validation_test(
        "Missing AWS_SECRET_ACCESS_KEY",
        {
            'AWS_REGION': 'us-east-1',
            'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE'
        },
        expected_success=False
    )
    
    # Test 6: Missing all required variables
    all_tests_passed &= run_validation_test(
        "Missing All Required Variables",
        {},
        expected_success=False
    )
    
    # Test 7: Empty string values
    all_tests_passed &= run_validation_test(
        "Empty String Values",
        {
            'AWS_REGION': '',
            'AWS_ACCESS_KEY_ID': '',
            'AWS_SECRET_ACCESS_KEY': ''
        },
        expected_success=False
    )
    
    # Final results
    print(f"\n{'='*80}")
    print("Test Summary")
    print(f"{'='*80}")
    if all_tests_passed:
        print("✓ All tests PASSED")
        return 0
    else:
        print("✗ Some tests FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())
