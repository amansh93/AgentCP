"""
LangGraph Nodes

This module contains all the LangGraph nodes that mirror the functionality
of the original AgentCP components.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
from .state import AgentState, WorkspaceManager
from agent.multi_step_planner import MultiStepPlanner
from agent.response_synthesizer import ResponseSynthesizer
from agent.workspace import AgentWorkspace
from agent.models import MultiStepPlan, PlanStep
from tools.query_tool import SimpleQueryTool, SimpleQueryInput, InformUserTool, InformUserInput
from tools.code_executor import describe_dataframe, execute_python_code
from tools.resolvers import get_valid_business_lines


class PlannerNode:
    """
    LangGraph node that mirrors MultiStepPlanner functionality.
    """
    
    def __init__(self):
        self.planner = MultiStepPlanner()
    
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Execute the planning phase."""
        print("\n--- LangGraph Planner: Creating multi-step plan ---")
        
        try:
            # Create the plan using the original planner
            plan = self.planner.create_plan(state["user_query"])
            
            return {
                "plan": plan,
                "status": "executing",
                "current_step_index": 0,
                "error_message": None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Planning failed: {str(e)}"
            }


class ExecutorNode:
    """
    LangGraph node that handles step execution.
    Mirrors the Executor functionality but works with individual steps.
    """
    
    def __init__(self):
        self.simple_query_tool = SimpleQueryTool()
        self.inform_user_tool = InformUserTool()
    
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Execute the current step."""
        
        # Check if we have a plan and current step
        if not state["plan"] or state["current_step_index"] >= len(state["plan"].plan):
            return {"status": "completed"}
        
        current_step = state["plan"].plan[state["current_step_index"]]
        summary = f"Step {state['current_step_index'] + 1}: {current_step.summary}"
        print(f"\n--- {summary} ---")
        
        try:
            # Execute the step based on tool type
            result = self._execute_step(state, current_step)
            
            # Update state with results
            new_summaries = state["summaries"].copy()
            new_summaries.append(summary)
            
            updates = {
                "summaries": new_summaries,
                "current_step_index": state["current_step_index"] + 1,
                "retry_count": 0,
                "error_message": None,
                "current_step": current_step
            }
            
            # Merge any additional updates from step execution
            updates.update(result)
            
            return updates
            
        except Exception as e:
            print(f"--- Step Failed: {str(e)} ---")
            
            # Handle retries
            retry_count = state["retry_count"] + 1
            
            if retry_count >= state["max_retries"]:
                return {
                    "status": "error",
                    "error_message": f"Step failed after {state['max_retries']} retries: {str(e)}",
                    "retry_count": retry_count
                }
            else:
                return {
                    "retry_count": retry_count,
                    "error_message": str(e),
                    "status": "executing"  # Stay in executing state for retry
                }
    
    def _execute_step(self, state: AgentState, step: PlanStep) -> Dict[str, Any]:
        """Execute a single step and return state updates."""
        tool_name = step.tool_name
        params = step.parameters
        
        if tool_name == "data_fetch":
            # Execute data fetch
            query_input = SimpleQueryInput(**params.dict(exclude={'output_variable'}))
            result_df = self.simple_query_tool.execute(query_input)
            
            # Add to workspace
            WorkspaceManager.add_dataframe(state, params.output_variable, result_df)
            return {}
            
        elif tool_name == "inform_user":
            # Execute inform user
            tool_input = InformUserInput(**params.dict())
            message = self.inform_user_tool.execute(tool_input)
            
            # This is a terminal step
            return {
                "terminal_message": message,
                "status": "completed"
            }
            
        elif tool_name == "describe_dataframe":
            # Execute describe dataframe
            # Create a temporary workspace for the describe function
            temp_workspace = AgentWorkspace()
            temp_workspace.dataframes = WorkspaceManager.get_dataframes_for_execution(state)
            
            description = describe_dataframe(temp_workspace, params.df_name)
            print(f"Description of '{params.df_name}':\\n{description}")
            return {}
            
        elif tool_name == "get_valid_business_lines":
            # Execute get valid business lines
            valid_lines = get_valid_business_lines()
            print(f"Valid business lines: {valid_lines}")
            return {}
            
        elif tool_name == "code_executor":
            # Execute code
            temp_workspace = AgentWorkspace()
            temp_workspace.dataframes = WorkspaceManager.get_dataframes_for_execution(state)
            
            updated_workspace = execute_python_code(temp_workspace, params.code)
            
            # Update state with new dataframes
            for name, df in updated_workspace.dataframes.items():
                WorkspaceManager.add_dataframe(state, name, df)
            
            return {}
            
        else:
            raise ValueError(f"Unknown tool_name: {tool_name}")


class ErrorHandlerNode:
    """
    LangGraph node that handles error recovery and plan correction.
    """
    
    def __init__(self):
        self.planner = MultiStepPlanner()
    
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Handle errors and generate corrected plan."""
        print("--- Requesting a new plan from the planner... ---")
        
        # Build correction prompt
        current_step = state.get("current_step")
        step_summary = current_step.summary if current_step else "Unknown step"
        
        correction_prompt = f"""
The previous plan failed during a step. Your task is to create a new plan to achieve the original user goal.

**Original User Query:** {state["user_query"]}

**Previous Plan Context:**
The plan was executing step {state["current_step_index"] + 1}, which was: "{step_summary}"
It failed with the error: {state["error_message"]}

**Current Workspace State:**
The following dataframes are available: {WorkspaceManager.list_dataframes(state)}

Please create a new, corrected plan to recover from this error and complete the original request.
"""
        
        try:
            # Get new plan
            new_plan = self.planner.create_plan(correction_prompt)
            
            # Replace remaining steps with new plan
            remaining_steps = new_plan.plan
            corrected_plan = MultiStepPlan(
                plan=state["plan"].plan[:state["current_step_index"]] + remaining_steps
            )
            
            print("--- Plan has been corrected. Retrying from the current step. ---")
            
            return {
                "plan": corrected_plan,
                "status": "executing",
                "retry_count": 0,
                "error_message": None
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error_message": f"Plan correction failed: {str(e)}"
            }


class ResponseSynthesizerNode:
    """
    LangGraph node that mirrors ResponseSynthesizer functionality.
    """
    
    def __init__(self):
        self.synthesizer = ResponseSynthesizer()
    
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Generate the final response."""
        print("\n--- LangGraph ResponseSynthesizer: Generating final response ---")
        
        try:
            # Create a temporary workspace for the synthesizer
            temp_workspace = AgentWorkspace()
            temp_workspace.dataframes = WorkspaceManager.get_dataframes_for_execution(state)
            
            # Generate response
            final_answer = self.synthesizer.synthesize(state["user_query"], temp_workspace)
            
            return {
                "final_response": final_answer,
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Response synthesis failed: {str(e)}"
            }


# Condition functions for workflow routing

def should_continue_execution(state: AgentState) -> str:
    """Determine next step in workflow."""
    status = state["status"]
    
    if status == "planning":
        return "plan"
    elif status == "executing":
        # Check if we have more steps
        if not state["plan"] or state["current_step_index"] >= len(state["plan"].plan):
            return "synthesize"
        else:
            return "execute"
    elif status == "error":
        # Check if we've exceeded retries
        if state["retry_count"] >= state["max_retries"]:
            return "handle_error"
        else:
            return "execute"  # Retry current step
    elif status == "completed":
        # Check if we have a terminal message
        if state.get("terminal_message"):
            return "end"
        else:
            return "synthesize"
    elif status == "failed":
        return "end"
    else:
        return "end"


def should_end(state: AgentState) -> bool:
    """Check if workflow should end."""
    return state["status"] in ["completed", "failed"] and (
        state.get("final_response") is not None or 
        state.get("terminal_message") is not None
    )