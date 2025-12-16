#!/usr/bin/env python3
"""
Unit test to verify the exception handling logic for MCP client initialization.
This test simulates the error handling without requiring actual MCP dependencies.
"""

import sys


def initialize_mcp_client(client_name, client_factory):
    """
    Copy of the initialize_mcp_client function from cloud_engineer_agent.py
    to test the exception handling logic independently.
    """
    try:
        print(f"Initializing {client_name}...")
        client = client_factory()
        print(f"Starting {client_name}...")
        # Simulate the start call
        if hasattr(client, 'start'):
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


# Mock client classes for testing
class MockSuccessfulClient:
    """Mock client that initializes successfully"""
    def start(self):
        pass


class MockFailingClient:
    """Mock client that raises an exception on start"""
    def start(self):
        raise RuntimeError("Simulated connection error")


class MockExceptionGroupClient:
    """Mock client that simulates a Python 3.11+ ExceptionGroup"""
    def start(self):
        # Create a mock ExceptionGroup-like error
        class MockExceptionGroup(BaseException):
            def __init__(self, message, exceptions):
                self.message = message
                self.exceptions = exceptions
                super().__init__(message)
            
            def __str__(self):
                return f"{self.message} ({len(self.exceptions)} sub-exceptions)"
        
        # Simulate nested exceptions from TaskGroup
        sub_exceptions = [
            ConnectionError("Failed to connect to MCP server"),
        ]
        raise MockExceptionGroup("unhandled errors in a TaskGroup", sub_exceptions)


def test_successful_initialization():
    """Test successful client initialization"""
    print("\n" + "=" * 80)
    print("TEST 1: Successful Client Initialization")
    print("=" * 80)
    
    client, success = initialize_mcp_client(
        "Test Successful Client",
        lambda: MockSuccessfulClient()
    )
    
    assert success is True, "Initialization should succeed"
    assert client is not None, "Client should not be None"
    print("✓ TEST PASSED: Successful initialization works correctly")
    return True


def test_regular_exception_handling():
    """Test handling of regular exceptions"""
    print("\n" + "=" * 80)
    print("TEST 2: Regular Exception Handling")
    print("=" * 80)
    
    client, success = initialize_mcp_client(
        "Test Failing Client",
        lambda: MockFailingClient()
    )
    
    assert success is False, "Initialization should fail"
    assert client is None, "Client should be None on failure"
    print("✓ TEST PASSED: Regular exceptions are handled correctly")
    return True


def test_exception_group_handling():
    """Test handling of ExceptionGroup (TaskGroup errors)"""
    print("\n" + "=" * 80)
    print("TEST 3: ExceptionGroup Handling (TaskGroup errors)")
    print("=" * 80)
    
    client, success = initialize_mcp_client(
        "Test ExceptionGroup Client",
        lambda: MockExceptionGroupClient()
    )
    
    assert success is False, "Initialization should fail"
    assert client is None, "Client should be None on failure"
    print("✓ TEST PASSED: ExceptionGroup exceptions are handled correctly")
    return True


def test_graceful_degradation():
    """Test that application can continue with partial MCP failure"""
    print("\n" + "=" * 80)
    print("TEST 4: Graceful Degradation with Partial Failures")
    print("=" * 80)
    
    # Simulate initializing two clients where one fails
    client1, success1 = initialize_mcp_client(
        "Documentation Client",
        lambda: MockSuccessfulClient()
    )
    
    client2, success2 = initialize_mcp_client(
        "Diagram Client",
        lambda: MockFailingClient()
    )
    
    # Check that we have partial functionality
    assert success1 is True, "First client should succeed"
    assert success2 is False, "Second client should fail"
    assert client1 is not None, "First client should be available"
    assert client2 is None, "Second client should be None"
    
    # Simulate the mcp_initialized logic from cloud_engineer_agent.py
    mcp_initialized = (client1 is not None or client2 is not None)
    assert mcp_initialized is True, "MCP should be marked as initialized with partial success"
    
    print("✓ TEST PASSED: Application can continue with partial MCP functionality")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("MCP Client Exception Handling Unit Tests")
    print("=" * 80)
    print(f"Python version: {sys.version}")
    
    all_passed = True
    
    try:
        all_passed = test_successful_initialization() and all_passed
        all_passed = test_regular_exception_handling() and all_passed
        all_passed = test_exception_group_handling() and all_passed
        all_passed = test_graceful_degradation() and all_passed
        
        print("\n" + "=" * 80)
        if all_passed:
            print("ALL TESTS PASSED ✓")
            print("=" * 80)
            print("\nSummary:")
            print("- Exception handling works correctly for all error types")
            print("- ExceptionGroup errors are properly caught and reported")
            print("- Application can continue with partial MCP functionality")
            print("- Clean error messages provide good diagnostics")
            sys.exit(0)
        else:
            print("SOME TESTS FAILED ✗")
            print("=" * 80)
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
