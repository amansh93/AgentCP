import os
from openai import OpenAI
from dotenv import load_dotenv
import json

from tools.query_tool import SimpleQueryInput

class Planner:
    """
    The Planner is the first "brain" of the agent.
    It uses an LLM to translate a natural language query into a structured
    plan (a SimpleQueryInput object) that can be executed by our tools.
    """
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """
        Creates a dynamic system prompt that includes the JSON schema
        of the tool's input model. This is a powerful way to guide the LLM.
        """
        schema = SimpleQueryInput.model_json_schema()
        
        prompt = f"""
You are an expert financial analyst assistant. Your task is to translate a user's natural language question into a structured JSON object.
The user's query will be about revenues or balances for financial clients.

You must respond with a single, valid JSON object that conforms to the following JSON Schema:
{json.dumps(schema, indent=2)}

Key considerations:
- 'metric': Determine if the user is asking about 'revenues' or 'balances'.
- 'entities': Extract all client names or group names mentioned. Do not resolve them, just extract the strings.
- 'date_description': Extract the raw date phrase the user provides (e.g., "last year", "Q1 2024").
- 'business' and 'subbusiness': Extract these if mentioned. If they are not mentioned, do not add them to the JSON.
- 'granularity': Infer the required granularity. If the user asks for a total, use 'aggregate'. If they ask for a list of clients, use 'client'. If they ask for a time series, use 'date'.

Respond with ONLY the JSON object. Do not include any other text, greetings, or explanations.
"""
        return prompt

    def create_plan(self, user_query: str) -> SimpleQueryInput:
        """
        Takes a user query, calls the LLM, and parses the response into a
        SimpleQueryInput object.
        """
        print("\n--- Planner: Creating a plan ---")
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": user_query}
            ],
            response_format={"type": "json_object"}
        )
        
        response_json = json.loads(response.choices[0].message.content)
        print(f"LLM Raw Response:\n{json.dumps(response_json, indent=2)}")
        
        # Pydantic automatically validates the JSON against our model
        plan = SimpleQueryInput.model_validate(response_json)
        
        print("--- Planner: Plan created successfully ---")
        return plan 