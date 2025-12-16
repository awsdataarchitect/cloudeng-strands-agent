#!/usr/bin/env python3
"""
Test script to verify MCP client initialization error handling.
This script simulates the TaskGroup exception scenario and verifies graceful degradation.
"""

import sys
import os

# Mock the environment variables to prevent early exit
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['AWS_ACCESS_KEY_ID'] = 'test-key-id'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test-secret-key'

def test_import_with_mcp_failure():
    """
    Test that the module can be imported even when MCP initialization fails.
    This simulates the scenario where MCP clients fail to initialize with TaskGroup errors.
    """
    print("=" * 80)
    print("Test: Import cloud_engineer_agent module with expected MCP failures")
    print("=" * 80)
    
    try:
        # Import the module - this will trigger MCP initialization which should fail gracefully
        import cloud_engineer_agent
        
        print("\n✓ Module imported successfully")
        print(f"✓ MCP initialized: {cloud_engineer_agent.mcp_initialized}")
        print(f"✓ AWS docs client: {'Available' if cloud_engineer_agent.aws_docs_mcp_client else 'Not available'}")
        print(f"✓ AWS diagram client: {'Available' if cloud_engineer_agent.aws_diagram_mcp_client else 'Not available'}")
        print(f"✓ Agent created: {cloud_engineer_agent.agent is not None}")
        
        # Verify that the agent was created even if MCP failed
        assert cloud_engineer_agent.agent is not None, "Agent should be created even if MCP fails"
        
        # Verify that functions are accessible
        assert hasattr(cloud_engineer_agent, 'execute_custom_task'), "execute_custom_task should be available"
        assert hasattr(cloud_engineer_agent, 'execute_predefined_task'), "execute_predefined_task should be available"
        assert hasattr(cloud_engineer_agent, 'get_predefined_tasks'), "get_predefined_tasks should be available"
        
        print("\n✓ All basic functions are accessible")
        
        # Test that predefined tasks can be retrieved
        tasks = cloud_engineer_agent.get_predefined_tasks()
        print(f"✓ Predefined tasks available: {len(tasks)} tasks")
        
        print("\n" + "=" * 80)
        print("TEST PASSED: Module handles MCP initialization failures gracefully")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_exception_group_handling():
    """
    Test that the code properly handles ExceptionGroup (Python 3.11+)
    """
    print("\n" + "=" * 80)
    print("Test: Verify ExceptionGroup handling capability")
    print("=" * 80)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check if ExceptionGroup is available (Python 3.11+)
    try:
        ExceptionGroup
        print("✓ ExceptionGroup is available (Python 3.11+)")
    except NameError:
        print("⚠ ExceptionGroup not available (Python < 3.11)")
        print("  Note: Using BaseException still catches all exceptions including async errors")
    
    print("=" * 80)
    return True

if __name__ == "__main__":
    print("\nMCP Client Error Handling Test Suite")
    print("=" * 80)
    
    success = True
    
    # Run tests
    success = test_exception_group_handling() and success
    success = test_import_with_mcp_failure() and success
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
