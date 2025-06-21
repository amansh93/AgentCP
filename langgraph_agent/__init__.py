"""
LangGraph Agent Package

This package contains a parallel implementation of the AgentCP workflow using LangGraph.
It mirrors the same architecture as the original but uses LangGraph's graph-based execution model.
"""

from .main import main_langgraph, compare_with_original
from .workflow import create_workflow
from .state import AgentState, create_initial_state, WorkspaceManager
from .nodes import (
    PlannerNode,
    ExecutorNode, 
    ErrorHandlerNode,
    ResponseSynthesizerNode
)

__version__ = "1.0.0"
__all__ = [
    "main_langgraph",
    "compare_with_original", 
    "create_workflow",
    "AgentState",
    "create_initial_state",
    "WorkspaceManager",
    "PlannerNode",
    "ExecutorNode",
    "ErrorHandlerNode", 
    "ResponseSynthesizerNode"
]