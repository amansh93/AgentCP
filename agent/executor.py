from .models import MultiStepPlan
from .workspace import AgentWorkspace
from .multi_step_planner import MultiStepPlanner
from tools.query_tool import SimpleQueryTool, SimpleQueryInput
from tools.code_executor import describe_dataframe, execute_python_code
from tools.resolvers import get_valid_business_lines

class HumanInterventionRequired(Exception):
    """Custom exception to signal that the agent is stuck and needs help."""
    def __init__(self, message="Agent requires human intervention.", context=None):
        self.message = message
        self.context = context
        super().__init__(self.message)

class Executor:
    """
    The Executor is the "doer" of the agent. It takes a multi-step plan
    and executes it step-by-step, with a self-correction loop.
    """
    def __init__(self, planner: MultiStepPlanner):
        self.workspace = AgentWorkspace()
        self.simple_query_tool = SimpleQueryTool()
        self.planner = planner
        print("--- Executor initialized ---")

    def execute_plan(self, initial_plan: MultiStepPlan, user_query: str):
        """
        Iterates through a dynamic plan, executing each step and returning
        the final workspace and a list of step summaries.
        """
        plan_steps = list(initial_plan.plan)
        summaries = []
        current_step_index = 0
        max_retries = 2 # Max retries per step
        retries = 0

        while current_step_index < len(plan_steps):
            step = plan_steps[current_step_index]
            summary = f"Step {current_step_index + 1}: {step.summary}"
            print(f"\n--- {summary} ---")
            summaries.append(summary)

            tool_name = step.tool_name
            params = step.parameters
            
            try:
                if tool_name == "data_fetch":
                    query_input = SimpleQueryInput(**params.dict(exclude={'output_variable'}))
                    result_df = self.simple_query_tool.execute(query_input)
                    self.workspace.add_df(params.output_variable, result_df)
                
                elif tool_name == "describe_dataframe":
                    description = describe_dataframe(self.workspace, params.df_name)
                    print(f"Description of '{params.df_name}':\n{description}")

                elif tool_name == "get_valid_business_lines":
                    valid_lines = get_valid_business_lines()
                    print(f"Valid business lines: {valid_lines}")

                elif tool_name == "code_executor":
                    # The code executor is the only tool with a retry loop
                    self.workspace = execute_python_code(self.workspace, params.code)
                
                else:
                    raise ValueError(f"Unknown tool_name: {tool_name}")

                # Successful execution, reset retry counter and move to next step
                retries = 0
                current_step_index += 1

            except Exception as e:
                error_message = str(e)
                print(f"--- Step Failed: {error_message} ---")
                
                retries += 1
                if retries >= max_retries:
                    context = {
                        "original_query": user_query,
                        "failed_step": step.summary,
                        "error_message": error_message,
                        "workspace_summary": self.workspace.list_dfs(),
                    }
                    raise HumanInterventionRequired(context=context)

                correction_prompt = f"""
The previous plan failed during a step. Your task is to create a new plan to achieve the original user goal.

**Original User Query:** {user_query}

**Previous Plan Context:**
The plan was executing step {current_step_index + 1}, which was: "{step.summary}"
It failed with the error: {error_message}

**Current Workspace State:**
The following dataframes are available: {self.workspace.list_dfs()}

Please create a new, corrected plan to recover from this error and complete the original request.
"""
                print("--- Requesting a new plan from the planner... ---")
                new_plan = self.planner.create_plan(correction_prompt)
                
                # Replace the rest of the plan with the new one
                plan_steps = plan_steps[:current_step_index] + new_plan.plan
                print("--- Plan has been corrected. Retrying from the current step. ---")
                # Do not increment step index, so we retry the corrected step
        
        print("\n--- Executor: Plan execution finished ---")
        return self.workspace, summaries 