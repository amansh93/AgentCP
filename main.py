from agent.multi_step_planner import MultiStepPlanner
from agent.executor import Executor
from agent.response_synthesizer import ResponseSynthesizer

def main_complex():
    """
    Main orchestration logic for a complex, multi-step query workflow.
    """
    # 1. Instantiate the agent components
    planner = MultiStepPlanner()
    executor = Executor(planner)
    synthesizer = ResponseSynthesizer()

    # 2. Define a complex user query
    user_query = "What were the top 3 systematic clients by revenue growth between last year and this year?"
    
    # 3. The Planner translates the query into a multi-step plan
    try:
        plan = planner.create_plan(user_query)
    except Exception as e:
        print(f"\n--- Error creating plan: {e} ---")
        return

    # 4. The Executor executes the plan
    try:
        final_workspace, summaries, message = executor.execute_plan(plan, user_query)

        if message:
            print("\n\n==================== AGENT RESPONSE ====================")
            print(message)
            print("========================================================")
            return
        
        # 5. The Synthesizer generates the final response
        final_answer = synthesizer.synthesize(user_query, final_workspace)

        print("\n\n==================== FINAL ANSWER ====================")
        print(final_answer)
        print("======================================================")

    except Exception as e:
        print(f"\n--- Error executing plan: {e} ---")


if __name__ == "__main__":
    main_complex() 