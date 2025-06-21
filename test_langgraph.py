"""
LangGraph Implementation Test

This test demonstrates the LangGraph workflow structure without requiring
API keys or actual LLM calls.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_agent.state import create_initial_state, WorkspaceManager
from langgraph_agent.workflow import SimplifiedLangGraphWorkflow
import pandas as pd


def test_state_management():
    """Test the state management functionality."""
    print("\\n=== Testing State Management ===")
    
    # Create initial state
    state = create_initial_state("Test query")
    print(f"Initial state created with query: {state['user_query']}")
    print(f"Initial status: {state['status']}")
    print(f"Initial dataframes: {len(state['dataframes'])}")
    
    # Test adding dataframes
    test_df = pd.DataFrame({'test': [1, 2, 3], 'data': ['a', 'b', 'c']})
    WorkspaceManager.add_dataframe(state, 'test_df', test_df)
    
    print(f"After adding dataframe: {len(state['dataframes'])} dataframes")
    print(f"Dataframe list: {WorkspaceManager.list_dataframes(state)}")
    
    # Test retrieving dataframes
    retrieved_df = WorkspaceManager.get_dataframe(state, 'test_df')
    print(f"Retrieved dataframe shape: {retrieved_df.shape}")
    
    return True


def test_workflow_structure():
    """Test the workflow structure."""
    print("\\n=== Testing Workflow Structure ===")
    
    # Create workflow
    workflow = SimplifiedLangGraphWorkflow()
    print("Workflow created successfully")
    
    # Test that all nodes are initialized
    assert workflow.planner_node is not None, "Planner node not initialized"
    assert workflow.executor_node is not None, "Executor node not initialized" 
    assert workflow.error_handler_node is not None, "Error handler node not initialized"
    assert workflow.response_synthesizer_node is not None, "Response synthesizer node not initialized"
    
    print("All nodes initialized successfully")
    return True


def test_workflow_logic():
    """Test the workflow execution logic without actual LLM calls."""
    print("\\n=== Testing Workflow Logic ===")
    
    # Create a mock state that simulates successful planning
    state = create_initial_state("Mock query for testing")
    
    # Test planning state
    from langgraph_agent.nodes import should_continue_execution
    
    state["status"] = "planning"
    next_action = should_continue_execution(state)
    print(f"From planning state, next action: {next_action}")
    assert next_action == "plan", f"Expected 'plan', got '{next_action}'"
    
    # Test executing state
    state["status"] = "executing"
    state["plan"] = type('MockPlan', (), {'plan': [1, 2, 3]})()  # Mock plan with 3 steps
    state["current_step_index"] = 0
    next_action = should_continue_execution(state)
    print(f"From executing state (step 0/3), next action: {next_action}")
    assert next_action == "execute", f"Expected 'execute', got '{next_action}'"
    
    # Test completion
    state["current_step_index"] = 3  # Beyond last step
    next_action = should_continue_execution(state)
    print(f"From executing state (all steps done), next action: {next_action}")
    assert next_action == "synthesize", f"Expected 'synthesize', got '{next_action}'"
    
    # Test completed state
    state["status"] = "completed"
    next_action = should_continue_execution(state)
    print(f"From completed state, next action: {next_action}")
    assert next_action == "synthesize", f"Expected 'synthesize', got '{next_action}'"
    
    print("Workflow logic tests passed")
    return True


def test_integration():
    """Test the full integration without external dependencies."""
    print("\\n=== Testing Integration ===")
    
    try:
        # Import all components
        from langgraph_agent import (
            main_langgraph, 
            create_workflow,
            AgentState,
            create_initial_state,
            WorkspaceManager
        )
        
        print("All imports successful")
        
        # Create workflow
        workflow = create_workflow()
        print("Workflow creation successful")
        
        # Test state creation
        test_state = create_initial_state("Integration test query")
        print(f"State creation successful: {test_state['user_query']}")
        
        print("Integration test passed")
        return True
        
    except Exception as e:
        print(f"Integration test failed: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("\\n" + "="*60)
    print("         LANGGRAPH IMPLEMENTATION TESTS")
    print("="*60)
    
    tests = [
        ("State Management", test_state_management),
        ("Workflow Structure", test_workflow_structure), 
        ("Workflow Logic", test_workflow_logic),
        ("Integration", test_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
    
    # Print results
    print("\\n=== Test Results ===")
    for test_name, passed, error in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
        if error:
            print(f"  Error: {error}")
    
    # Summary
    passed_count = sum(1 for _, passed, _ in results if passed)
    total_count = len(results)
    print(f"\\nSummary: {passed_count}/{total_count} tests passed")
    
    return passed_count == total_count


if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print("\\n✓ All tests passed! LangGraph implementation is ready.")
    else:
        print("\\n✗ Some tests failed. Please check the implementation.")