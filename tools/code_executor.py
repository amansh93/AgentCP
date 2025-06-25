from typing import Dict
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import time

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
        
        # CRITICAL: Verify the file was actually saved where expected
        if not os.path.exists(save_path):
            # If the file wasn't saved at the expected location, check for temp files
            import tempfile
            temp_dir = tempfile.gettempdir()
            print(f"WARNING: Plot was not saved to expected location: {save_path}")
            print(f"Check temp directory: {temp_dir}")
            
            # Try to find matplotlib temp files
            import glob
            temp_files = glob.glob(os.path.join(temp_dir, "*.png"))
            recent_temp_files = [f for f in temp_files if os.path.getmtime(f) > (time.time() - 60)]  # Files created in last minute
            
            if recent_temp_files:
                actual_file = max(recent_temp_files, key=os.path.getmtime)  # Most recent
                print(f"Found recent temp file: {actual_file}")
                print(f"Attempting to move to correct location...")
                
                try:
                    import shutil
                    shutil.move(actual_file, save_path)
                    print(f"Successfully moved file to: {save_path}")
                except Exception as move_error:
                    print(f"Failed to move file: {move_error}")
                    save_path = actual_file  # Use the temp location as fallback
                    print(f"Using temp file location: {save_path}")
            else:
                # Generate a new unique filename and try again
                timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include microseconds
                backup_path = f'static/plots/timeseries_backup_{timestamp}.png'
                print(f"No temp files found. Regenerating plot at: {backup_path}")
                
                # Re-create the plot with new path
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
                
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                plt.savefig(backup_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                if os.path.exists(backup_path):
                    save_path = backup_path
                    print(f"Successfully saved backup plot to: {save_path}")
                else:
                    raise Exception(f"Failed to save plot at both {save_path} and {backup_path}")
        else:
            print(f"✓ Plot successfully saved to: {save_path}")
        
        # IMPORTANT: Print the actual file location for LLM visibility
        print(f"📁 PLOT FILE LOCATION: {save_path}")
        print(f"   Use this exact path in your dataframe: {save_path}")
        
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
    
    # CRITICAL: Validate any plot files referenced in dataframes actually exist
    for df_name, df in workspace.dataframes.items():
        if isinstance(df, pd.DataFrame) and 'plot_path' in df.columns:
            for plot_path in df['plot_path'].dropna():
                if not os.path.exists(plot_path):
                    print(f"WARNING: Plot file does not exist at reported path: {plot_path}")
                    
                    # Try to find the file in temp directories
                    import tempfile
                    import glob
                    temp_dir = tempfile.gettempdir()
                    temp_files = glob.glob(os.path.join(temp_dir, "*.png"))
                    recent_temp_files = [f for f in temp_files if os.path.getmtime(f) > (time.time() - 120)]  # Files created in last 2 minutes
                    
                    if recent_temp_files:
                        actual_file = max(recent_temp_files, key=os.path.getmtime)
                        print(f"Found potential temp file: {actual_file}")
                        print(f"This file was likely created instead of: {plot_path}")
                        
                        # Update the dataframe with the actual file location
                        df.loc[df['plot_path'] == plot_path, 'plot_path'] = actual_file
                        print(f"Updated dataframe to reference actual file location: {actual_file}")
                    else:
                        print(f"ERROR: No recent temp files found. Plot may have failed silently.")
                else:
                    print(f"✓ Verified plot file exists: {plot_path}")
    
    print("--- Code Execution Finished ---")
    return workspace 