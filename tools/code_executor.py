from typing import Dict
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

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
    
    Available imports: pandas as pd, matplotlib.pyplot as plt, numpy as np
    Available utilities: plot_timeseries() function for easy time series plotting
    """
    print(f"--- Executing Python Code ---\n{code}\n---------------------------")
    
    # Time series plotting utility function
    def plot_timeseries(df, date_col='date', value_cols=None, title='Time Series Plot', 
                       figsize=(12, 6), save_path=None):
        """
        Utility function for creating professional time series plots.
        
        Args:
            df: DataFrame with time series data
            date_col: Name of the date column (default: 'date')
            value_cols: List of columns to plot, or None to auto-detect
            title: Plot title
            figsize: Figure size tuple
            save_path: Path to save the plot, or None to auto-generate
        
        Returns:
            Path to the saved plot file
        """
        # Ensure date column is datetime
        if date_col in df.columns:
            df = df.copy()
            df[date_col] = pd.to_datetime(df[date_col])
            df = df.sort_values(date_col)
        
        # Auto-detect value columns if not specified
        if value_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            value_cols = [col for col in numeric_cols if col != date_col]
        
        # Create the plot
        plt.figure(figsize=figsize)
        
        for col in value_cols:
            if col in df.columns:
                plt.plot(df[date_col], df[col], marker='o', label=col, linewidth=2)
        
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Generate save path if not provided
        if save_path is None:
            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            save_path = f'static/plots/timeseries_{timestamp}.png'
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()  # Important: close the figure to free memory
        
        return save_path
    
    # Create a local scope for the execution, pre-populated with workspace data and utilities
    local_scope = {
        'dataframes': workspace.dataframes, 
        'pd': pd,
        'plt': plt,
        'np': np,
        'plot_timeseries': plot_timeseries
    }
    
    # Execute the code
    try:
        exec(code, {'pd': pd, 'plt': plt, 'np': np, 'plot_timeseries': plot_timeseries}, local_scope)
    except Exception as e:
        print(f"--- Code Execution Error: {e} ---")
        raise
        
    # Update the workspace with the potentially modified dataframes
    workspace.dataframes = local_scope['dataframes']
    
    print("--- Code Execution Finished ---")
    return workspace 