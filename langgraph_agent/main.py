"""
LangGraph Agent Main Entry Point

This module provides the main entry point for the LangGraph-based agent.
It mirrors the functionality of the original main.py but uses the LangGraph workflow.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .workflow import create_workflow


def main_langgraph():
    """
    Main orchestration logic for the LangGraph-based agent.
    
    This mirrors the main_complex() function but uses LangGraph for execution.
    """
    print("\\n" + "="*60)
    print("         LANGGRAPH AGENT VERSION")
    print("="*60)
    
    # Create the LangGraph workflow
    workflow = create_workflow()
    
    # Define a complex user query (same as original)
    user_query = "What were the top 3 systematic clients by revenue growth between last year and this year?"
    
    print(f"\\nUser Query: {user_query}")
    
    # Execute the workflow
    try:
        final_state = workflow.run(user_query)
        
        # Display results
        if final_state.get("terminal_message"):
            print("\\n\\n==================== AGENT RESPONSE ====================")
            print(final_state["terminal_message"])
            print("========================================================")
            
        elif final_state.get("final_response"):
            print("\\n\\n==================== FINAL ANSWER ====================")
            print(final_state["final_response"])
            print("======================================================")
            
        else:
            print("\\n\\n==================== EXECUTION FAILED ====================")
            print(f"Status: {final_state.get('status', 'Unknown')}")
            print(f"Error: {final_state.get('error_message', 'No error message')}")
            print("=========================================================")
        
        # Print execution summary
        print("\\n--- Execution Summary ---")
        print(f"Status: {final_state.get('status')}")
        print(f"Steps executed: {len(final_state.get('summaries', []))}")
        print(f"Dataframes created: {len(final_state.get('dataframes', {}))}")
        if final_state.get('summaries'):
            print("Step summaries:")
            for i, summary in enumerate(final_state['summaries'], 1):
                print(f"  {i}. {summary}")
                
    except Exception as e:
        print(f"\\n--- Error executing LangGraph workflow: {e} ---")
        import traceback
        traceback.print_exc()


def compare_with_original():
    """
    Function to demonstrate the differences between original and LangGraph versions.
    """
    print("\\n" + "="*60)
    print("         COMPARISON: ORIGINAL vs LANGGRAPH")
    print("="*60)
    
    print("""
ORIGINAL ARCHITECTURE:
├── MultiStepPlanner (creates plan)
├── Executor (sequential execution)
│   ├── Step 1 → Tool execution
│   ├── Step 2 → Tool execution  
│   └── Step N → Tool execution
└── ResponseSynthesizer (final response)

LANGGRAPH ARCHITECTURE:
├── PlannerNode (creates plan)
├── Workflow Graph:
│   ├── ExecutorNode (step execution)
│   ├── ConditionalEdges (routing logic)
│   ├── ErrorHandlerNode (error recovery)
│   └── Loops until completion
└── ResponseSynthesizerNode (final response)

KEY DIFFERENCES:
✓ Graph-based vs Sequential execution
✓ Built-in state management
✓ More flexible error handling and recovery
✓ Conditional routing between nodes
✓ Better support for parallel execution
✓ Enhanced debugging and observability
""")


if __name__ == "__main__":
    # Run the LangGraph version
    main_langgraph()
    
    # Show comparison
    compare_with_original()