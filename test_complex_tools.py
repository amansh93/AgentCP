import pandas as pd
from agent.workspace import AgentWorkspace
from tools.code_executor import describe_dataframe, execute_python_code

def run_complex_tool_tests():
    """
    Tests the AgentWorkspace and the PythonCodeExecutor tool.
    """
    print("--- Running Complex Tool Tests ---")

    # --- Test Case 1: Workspace functionality ---
    print("\n--- Test Case 1: Workspace add, get, and list ---")
    workspace = AgentWorkspace()
    sample_df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    workspace.add_df("test_df", sample_df)
    
    retrieved_df = workspace.get_df("test_df")
    assert retrieved_df.equals(sample_df), "Workspace get_df failed"
    
    df_list = workspace.list_dfs()
    assert "test_df" in df_list, "Workspace list_dfs failed"
    print("Workspace tests PASSED")

    # --- Test Case 2: describe_dataframe tool ---
    print("\n--- Test Case 2: describe_dataframe tool ---")
    description = describe_dataframe(workspace, "test_df")
    print(f"Description:\n{description}")
    assert "'a'" in description and "'b'" in description, "describe_dataframe failed"
    print("describe_dataframe test PASSED")

    # --- Test Case 3: execute_python_code tool ---
    print("\n--- Test Case 3: execute_python_code tool ---")
    code_to_execute = """
# A new dataframe is created by transforming an existing one
df = dataframes['test_df']
new_df = df.copy()
new_df['c'] = new_df['a'] + new_df['b']
dataframes['new_test_df'] = new_df
"""
    workspace = execute_python_code(workspace, code_to_execute)
    
    # Verify the new dataframe exists in the workspace
    final_df_list = workspace.list_dfs()
    print(f"Final workspace contents: {final_df_list}")
    assert "new_test_df" in final_df_list, "Code executor did not add new df to workspace"
    
    # Verify the calculation was correct
    new_df = workspace.get_df("new_test_df")
    expected_df = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [4, 6]})
    assert new_df.equals(expected_df), "Calculation within code executor was incorrect"
    print("execute_python_code test PASSED")
    
    print("\n--- All Complex Tool Tests Passed ---")

if __name__ == "__main__":
    run_complex_tool_tests() 