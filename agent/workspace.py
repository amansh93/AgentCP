from typing import Dict
import pandas as pd

class AgentWorkspace:
    """
    A simple workspace for the agent to store intermediate dataframes.
    This acts as the agent's short-term memory during a multi-step task.
    """
    def __init__(self):
        self.dataframes: Dict[str, pd.DataFrame] = {}
        print("--- AgentWorkspace initialized ---")

    def add_df(self, name: str, df: pd.DataFrame):
        """Adds or updates a dataframe in the workspace."""
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Value added to workspace must be a pandas DataFrame, not {type(df)}")
        print(f"--- Workspace: Adding/updating dataframe '{name}' ---")
        self.dataframes[name] = df

    def get_df(self, name: str) -> pd.DataFrame:
        """Retrieves a dataframe from the workspace."""
        if name not in self.dataframes:
            raise KeyError(f"DataFrame '{name}' not found in workspace.")
        return self.dataframes[name]

    def list_dfs(self) -> Dict[str, str]:
        """Lists the dataframes in the workspace and their schemas."""
        return {name: str(df.columns.to_list()) for name, df in self.dataframes.items()} 