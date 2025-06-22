"""
LangGraph State Management

This module defines the state structure for the LangGraph-based agent.
It mirrors the functionality of AgentWorkspace but is designed for LangGraph's
state management system.
"""

from typing import Dict, List, Optional, Any, TypedDict
from pydantic import BaseModel
import pandas as pd
from agent.models import MultiStepPlan, PlanStep


class AgentState(TypedDict):
    """
    State structure for the LangGraph agent.
    
    This mirrors the AgentWorkspace functionality but is designed for
    LangGraph's state management system.
    """
    # Original user query
    user_query: str
    
    # Current execution plan
    plan: Optional[MultiStepPlan]
    
    # Current step index
    current_step_index: int
    
    # Dataframes storage (mirrors AgentWorkspace.dataframes)
    dataframes: Dict[str, Any]  # Will store serialized dataframes
    
    # Execution summaries
    summaries: List[str]
    
    # Current step being executed
    current_step: Optional[PlanStep]
    
    # Error handling
    error_message: Optional[str]
    retry_count: int
    max_retries: int
    
    # Final response
    final_response: Optional[str]
    
    # Execution status
    status: str  # "planning", "executing", "error", "completed", "failed"
    
    # Terminal message (for inform_user tool)
    terminal_message: Optional[str]


class WorkspaceManager:
    """
    Utility class to manage dataframes in the state.
    
    Provides similar functionality to AgentWorkspace but works with
    LangGraph's state management.
    """
    
    @staticmethod
    def add_dataframe(state: AgentState, name: str, df: pd.DataFrame) -> None:
        """Add a dataframe to the state."""
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Value must be a pandas DataFrame, not {type(df)}")
        
        # Convert DataFrame to dict for serialization
        state["dataframes"][name] = df.to_dict('records')
        print(f"--- Workspace: Adding/updating dataframe '{name}' ---")
    
    @staticmethod
    def get_dataframe(state: AgentState, name: str) -> pd.DataFrame:
        """Get a dataframe from the state."""
        if name not in state["dataframes"]:
            raise KeyError(f"DataFrame '{name}' not found in workspace.")
        
        # Convert back to DataFrame
        return pd.DataFrame(state["dataframes"][name])
    
    @staticmethod
    def list_dataframes(state: AgentState) -> Dict[str, str]:
        """List all dataframes in the state."""
        return {
            name: str(pd.DataFrame(data).columns.tolist()) 
            for name, data in state["dataframes"].items()
        }
    
    @staticmethod
    def get_dataframes_for_execution(state: AgentState) -> Dict[str, pd.DataFrame]:
        """Get all dataframes as pandas DataFrames for code execution."""
        return {
            name: pd.DataFrame(data) 
            for name, data in state["dataframes"].items()
        }


def create_initial_state(user_query: str) -> AgentState:
    """Create the initial state for a new agent execution."""
    return AgentState(
        user_query=user_query,
        plan=None,
        current_step_index=0,
        dataframes={},
        summaries=[],
        current_step=None,
        error_message=None,
        retry_count=0,
        max_retries=2,
        final_response=None,
        status="planning",
        terminal_message=None
    )