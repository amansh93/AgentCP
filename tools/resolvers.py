from typing import List, Dict, Set
from thefuzz import process
import re
import json
import os
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import datetime
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
from fuzzywuzzy import process
from knowledge_base.client_data import CLIENT_NAME_TO_ID, CLIENT_GROUP_TO_IDS, CLIENT_MAPPING, VALID_BUSINESSES, VALID_SUBBUSINESSES

class DateRange(BaseModel):
    start_date: str = Field(..., description="The start date in YYYY-MM-DD format.")
    end_date: str = Field(..., description="The end date in YYYY-MM-DD format.")

def _get_llm_date_range(date_description: str) -> (str, str):
    """(Internal) Use an LLM to parse a complex date description."""
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    schema = DateRange.model_json_schema()

    prompt = f"""
You are a date parsing expert. Your sole job is to convert a user's natural language date description into a precise start and end date.
The current date is {datetime.now().strftime('%Y-%m-%d')}.
You must respond with a single, valid JSON object that conforms to the following JSON Schema:
{json.dumps(schema, indent=2)}

User's request: "{date_description}"

Respond with ONLY the JSON object.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Cheaper and faster model is fine for this
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"}
        )
        response_json = json.loads(response.choices[0].message.content)
        date_range = DateRange.model_validate(response_json)
        return date_range.start_date, date_range.end_date
    except Exception as e:
        print(f"--- LLM Date Parsing failed: {e}. Raising exception. ---")
        raise

def resolve_clients(names: List[str]) -> List[str]:
    """
    Resolves a list of client or group names into a list of client IDs.

    - Handles fuzzy matching for typos.
    - Expands group names into their constituent client IDs.
    - Deduplicates the final list of IDs.
    """
    if not names:
        return []

    all_known_entities = list(CLIENT_NAME_TO_ID.keys()) + list(CLIENT_GROUP_TO_IDS.keys())
    resolved_ids: Set[str] = set()

    for name in names:
        # Standardize the input name
        clean_name = name.lower().strip()

        # Find the best match from our knowledge base
        best_match, score = process.extractOne(clean_name, all_known_entities)
        
        # We can tune this threshold
        if score < 80:
            print(f"Warning: Could not confidently match '{name}'. Ignoring.")
            continue

        # Check if the match is a group and expand it
        if best_match in CLIENT_GROUP_TO_IDS:
            resolved_ids.update(CLIENT_GROUP_TO_IDS[best_match])
        # Otherwise, assume it's an individual client
        elif best_match in CLIENT_NAME_TO_ID:
            resolved_ids.add(CLIENT_NAME_TO_ID[best_match])

    return list(resolved_ids)

def resolve_dates(date_description: str) -> (str, str):
    """
    Resolves a natural language date description into a start and end date.
    Tries fast, deterministic methods first, then falls back to an LLM.
    """
    today = datetime.now()
    clean_desc = date_description.lower().strip()

    # Fiscal Year (e.g., "fy'24", "fy2024")
    fy_match = re.search(r'fy\'?(\d{2,4})', clean_desc)
    if fy_match:
        year_suffix = int(fy_match.group(1))
        year = 2000 + year_suffix if year_suffix < 100 else year_suffix
        start_date = datetime(year - 1, 10, 1).strftime('%Y-%m-%d') # Assuming fiscal year starts in Oct
        end_date = datetime(year, 9, 30).strftime('%Y-%m-%d')
        return start_date, end_date

    # Quarter (e.g., "q1 2025", "qtr 1 2025", "q1'25")
    q_match = re.search(r'(?:q|qtr)\s?([1-4])\s?\'?(\d{2,4})', clean_desc)
    if q_match:
        quarter = int(q_match.group(1))
        year_suffix = int(q_match.group(2))
        year = 2000 + year_suffix if year_suffix < 100 else year_suffix
        start_month = (quarter - 1) * 3 + 1
        start_date = datetime(year, start_month, 1)
        end_date = start_date + relativedelta(months=3, days=-1)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

    # Specific Year (e.g., "2023")
    year_match = re.search(r'\b(20\d{2})\b', clean_desc)
    if year_match:
        year = int(year_match.group(1))
        start_date = datetime(year, 1, 1).strftime('%Y-%m-%d')
        end_date = datetime(year, 12, 31).strftime('%Y-%m-%d')
        return start_date, end_date

    # Relative terms
    if "last year" in clean_desc:
        last_year = today.year - 1
        return resolve_dates(str(last_year))
    if "this year" in clean_desc:
        return resolve_dates(str(today.year))

    # Fallback for simple dates
    try:
        # A simple phrase like "january 2024" might just resolve to a single day
        parsed_date = parse(clean_desc)
        # We'll assume the user meant the whole month in this case
        start_date = parsed_date.replace(day=1)
        end_date = start_date + relativedelta(months=1, days=-1)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    except ValueError:
        print(f"Warning: Could not parse date description '{date_description}'.")
        # Return a default range (e.g., this year to date)
        end_date = today.strftime('%Y-%m-%d')
        start_date = today.replace(day=1, month=1).strftime('%Y-%m-%d')
        return start_date, end_date

    # Fallback to LLM for complex cases
    try:
        print(f"--- Using LLM to parse date description: '{date_description}' ---")
        return _get_llm_date_range(date_description)
    except Exception:
        # If LLM fails, use a final fallback
        print(f"Warning: LLM date parsing failed for '{date_description}'. Using default.")
        end_date = today.strftime('%Y-%m-%d')
        start_date = today.replace(day=1, month=1).strftime('%Y-%m-%d')
        return start_date, end_date 

def get_valid_business_lines():
    """
    Returns a dictionary of valid business and sub-business lines.
    This is used to provide the planner with up-to-date knowledge.
    """
    return {
        "valid_businesses": VALID_BUSINESSES,
        "valid_subbusinesses": VALID_SUBBUSINESSES
    }

class ClientNameResolver:
    """
    Resolves client names and group names from natural language
    into lists of specific client IDs.
    """
    def __init__(self):
        self.client_names = CLIENT_MAPPING["names"]
        self.client_groups = CLIENT_MAPPING["groups"]
        self.all_client_ids = list(self.client_names.values())
        self.client_groups["all clients"] = self.all_client_ids

    def resolve(self, entity_names: list[str]) -> list[str]:
        resolved_ids = []
        for entity in entity_names:
            entity_lower = entity.lower()

            # First, check for an exact match in groups
            if entity_lower in self.client_groups:
                resolved_ids.extend(self.client_groups[entity_lower])
                continue

            # If not in groups, check for a fuzzy match in individual client names
            match, score = process.extractOne(entity_lower, self.client_names.keys())
            if score > 80: # Using a threshold of 80 for confidence
                resolved_ids.append(self.client_names[match])
            else:
                print(f"Warning: Could not resolve client name '{entity}'")

        # Return a unique list of IDs
        return list(set(resolved_ids))

def resolve_clients(entity_names: list[str]) -> list[str]:
    """
    Resolves a list of client or group names into a list of client IDs.

    - Handles fuzzy matching for typos.
    - Expands group names into their constituent client IDs.
    - Deduplicates the final list of IDs.
    """
    if not entity_names:
        return []

    all_known_entities = list(CLIENT_NAME_TO_ID.keys()) + list(CLIENT_GROUP_TO_IDS.keys())
    resolved_ids: Set[str] = set()

    for name in entity_names:
        # Standardize the input name
        clean_name = name.lower().strip()

        # Find the best match from our knowledge base
        best_match, score = process.extractOne(clean_name, all_known_entities)
        
        # We can tune this threshold
        if score < 80:
            print(f"Warning: Could not confidently match '{name}'. Ignoring.")
            continue

        # Check if the match is a group and expand it
        if best_match in CLIENT_GROUP_TO_IDS:
            resolved_ids.update(CLIENT_GROUP_TO_IDS[best_match])
        # Otherwise, assume it's an individual client
        elif best_match in CLIENT_NAME_TO_ID:
            resolved_ids.add(CLIENT_NAME_TO_ID[best_match])

    return list(resolved_ids)

def resolve_dates(date_description: str) -> tuple[str, str]:
    """
    Resolves a natural language date description into a start and end date.
    """
    today = datetime.now()
    clean_desc = date_description.lower().strip()

    # Fiscal Year (e.g., "fy'24", "fy2024")
    fy_match = re.search(r'fy\'?(\d{2,4})', clean_desc)
    if fy_match:
        year_suffix = int(fy_match.group(1))
        year = 2000 + year_suffix if year_suffix < 100 else year_suffix
        start_date = datetime(year - 1, 10, 1).strftime('%Y-%m-%d') # Assuming fiscal year starts in Oct
        end_date = datetime(year, 9, 30).strftime('%Y-%m-%d')
        return start_date, end_date

    # Quarter (e.g., "q1 2025", "qtr 1 2025", "q1'25")
    q_match = re.search(r'(?:q|qtr)\s?([1-4])\s?\'?(\d{2,4})', clean_desc)
    if q_match:
        quarter = int(q_match.group(1))
        year_suffix = int(q_match.group(2))
        year = 2000 + year_suffix if year_suffix < 100 else year_suffix
        start_month = (quarter - 1) * 3 + 1
        start_date = datetime(year, start_month, 1)
        end_date = start_date + relativedelta(months=3, days=-1)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

    # Specific Year (e.g., "2023")
    year_match = re.search(r'\b(20\d{2})\b', clean_desc)
    if year_match:
        year = int(year_match.group(1))
        start_date = datetime(year, 1, 1).strftime('%Y-%m-%d')
        end_date = datetime(year, 12, 31).strftime('%Y-%m-%d')
        return start_date, end_date

    # Relative terms
    if "last year" in clean_desc:
        last_year = today.year - 1
        return resolve_dates(str(last_year))
    if "this year" in clean_desc:
        return resolve_dates(str(today.year))

    # Fallback for simple dates
    try:
        # A simple phrase like "january 2024" might just resolve to a single day
        parsed_date = parse(clean_desc)
        # We'll assume the user meant the whole month in this case
        start_date = parsed_date.replace(day=1)
        end_date = start_date + relativedelta(months=1, days=-1)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    except ValueError:
        print(f"Warning: Could not parse date description '{date_description}'.")
        # Return a default range (e.g., this year to date)
        end_date = today.strftime('%Y-%m-%d')
        start_date = today.replace(day=1, month=1).strftime('%Y-%m-%d')
        return start_date, end_date

    # Fallback to LLM for complex cases
    try:
        print(f"--- Using LLM to parse date description: '{date_description}' ---")
        return _get_llm_date_range(date_description)
    except Exception:
        # If LLM fails, use a final fallback
        print(f"Warning: LLM date parsing failed for '{date_description}'. Using default.")
        end_date = today.strftime('%Y-%m-%d')
        start_date = today.replace(day=1, month=1).strftime('%Y-%m-%d')
        return start_date, end_date 