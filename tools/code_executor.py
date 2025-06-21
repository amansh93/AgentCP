from typing import Dict
import pandas as pd

from agent.workspace import AgentWorkspace

def describe_dataframe(workspace: AgentWorkspace, df_name: str) -> str:
    """
    Returns a string describing the schema of a dataframe in the workspace.
    This is a crucial tool for the Planner to write correct code.
    """
    print(f"--- Describing dataframe '{df_name}' ---")
    df = workspace.get_df(df_name)
    return f"DataFrame '{df_name}' has columns: {df.columns.to_list()} with dtypes:\n{df.dtypes}"

def execute_python_code(workspace: AgentWorkspace, code: str) -> AgentWorkspace:
    """
    Executes a string of Python code within the context of the agent's workspace.
    
    The code has access to a 'dataframes' dictionary, where keys are the names
    of the dataframes in the workspace and values are the pandas DataFrame objects.
    
    The code can modify this dictionary (e.g., add new dataframes or modify
    existing ones), and the modified dictionary is used to update the workspace.
    """
    print(f"--- Executing Python Code ---\n{code}\n---------------------------")
    
    # Create a local scope for the execution, pre-populated with workspace data
    local_scope = {'dataframes': workspace.dataframes, 'pd': pd}
    
    # Execute the code
    try:
        exec(code, {'pd': pd}, local_scope)
    except Exception as e:
        print(f"--- Code Execution Error: {e} ---")
        raise
        
    # Update the workspace with the potentially modified dataframes
    workspace.dataframes = local_scope['dataframes']
    
    print("--- Code Execution Finished ---")
    return workspace 