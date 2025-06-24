import json
import pandas as pd
from .llm_client import get_llm_client
from .config import SYNTHESIZER_MODEL
from .workspace import AgentWorkspace
from knowledge_base.client_data import CLIENT_URL_SKELETON

class ResponseSynthesizer:
    """
    Takes the final agent workspace and the original user query to synthesize
    a user-friendly, natural language response.
    """
    def __init__(self):
        self.client = get_llm_client()

    def _build_prompt(self, user_query: str, workspace: AgentWorkspace) -> str:
        """Builds the system prompt for the response synthesizer LLM."""
        
        # Convert dataframes to a string format for the prompt
        workspace_summary = "The following dataframes were generated to answer your query:\n"
        for name, df in workspace.dataframes.items():
            workspace_summary += f"\n--- Dataframe: '{name}' ---\n"
            workspace_summary += df.to_string()
            workspace_summary += "\n"

        prompt = f"""
You are an expert financial analyst assistant. Your task is to provide a clear, concise, and user-friendly answer to a user's question based on the data provided.

**Original User Query:** "{user_query}"

**Available Data:**
{workspace_summary}

**Your Task:**
1.  Analyze the original query and the available data.
2.  Formulate a direct answer to the user's question.
3.  If the final dataframe contains a 'client_id' and a 'client_name' column, generate a Markdown link for each client name using the skeleton: {CLIENT_URL_SKELETON}. For example, if the client name is 'Citadel' and the client_id is 'cl_id_citadel', the output should be '[Citadel](https://my-internal-platform.com/clients/cl_id_citadel)'.
4.  If the final dataframe contains a 'plot_path' column, you must embed the plot in your response using HTML image syntax with size constraints for better display in chat. Prepend a '/' to the path to make it absolute. For example: `<img src="/static/plots/plot_123.png" alt="Financial Plot" style="max-width: 800px; width: 100%; height: auto;">`. This ensures the plot displays at a reasonable size in the chat interface.
5.  If the query asks for a list or ranking (e.g., "top 3"), format your response as a Markdown table. Make sure column headers are clean and human-readable (e.g., 'Client Name' instead of 'client_name_last_year').
6.  If the query asks for a single number (e.g., "What were the total revenues?"), answer in a clear, natural language sentence. Format large numbers to be human-readable (e.g., write '$45.2 million' instead of '45200000').
7.  Begin with a concise summary of the findings. Do not just output a table without explanation.
8.  Do not mention the intermediate dataframes (e.g., 'rev_2023'). Only refer to the final, meaningful data.
9.  If you cannot answer the user's question with the available data, clearly state what information is missing. Conclude your response with the line: "Please reach out to [CA Strats](mailto:ca.strats@example.com) for further details."
10.  Be polite and helpful.
"""
        return prompt

    def synthesize(self, user_query: str, workspace: AgentWorkspace) -> str:
        """
        Generates the final natural language response.
        """
        print("\n--- Synthesizing Final Response ---")
        prompt = self._build_prompt(user_query, workspace)

        response = self.client.chat.completions.create(
            model=SYNTHESIZER_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful financial analyst assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
        )
        
        final_answer = response.choices[0].message.content
        print("--- Response Synthesis Finished ---")
        return final_answer 