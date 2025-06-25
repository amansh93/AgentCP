import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, request, jsonify
from agent.multi_step_planner import MultiStepPlanner
from agent.executor import Executor, HumanInterventionRequired
from agent.response_synthesizer import ResponseSynthesizer
from performance_flows_workflow import process_query_with_performance_flows

app = Flask(__name__)

# Initialize agent components once
planner = MultiStepPlanner()
executor = Executor(planner)
synthesizer = ResponseSynthesizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_query = request.json.get('query')
    use_performance_flows = request.json.get('use_performance_flows', False)
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Check which workflow to use
        if use_performance_flows:
            # Use Performance/Flows workflow
            perf_flows_response = process_query_with_performance_flows(user_query)
            
            return jsonify({
                "status": "success",
                "answer": perf_flows_response["text"],
                "reasoning_steps": ["Used Performance/Flows workflow"],
                "has_image": perf_flows_response["has_image"],
                "image_path": perf_flows_response["image_path"]
            })
        
        else:
            # Use Balances/Revs/Capital workflow
            # 1. Planner creates a plan
            plan = planner.create_plan(user_query)

            # 2. Executor executes the plan
            final_workspace, summaries, message = executor.execute_plan(plan, user_query)

            # If the executor returned a direct message, use it as the answer
            if message:
                return jsonify({
                    "status": "success",
                    "answer": message,
                    "reasoning_steps": summaries
                })

            # 3. Synthesizer generates the final response
            final_answer = synthesizer.synthesize(user_query, final_workspace)
            
            return jsonify({
                "status": "success",
                "answer": final_answer,
                "reasoning_steps": summaries
            })

    except HumanInterventionRequired as e:
        return jsonify({
            "status": "needs_human_input",
            "message": e.message,
            "context": e.context
        }), 200 # Return 200 OK as this is an expected state

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 