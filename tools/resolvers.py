from typing import List, Dict, Set
import re
import json
import os
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import datetime
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

# Use rapidfuzz for string matching
from rapidfuzz import process, fuzz

from knowledge_base.client_data import CLIENT_NAME_TO_ID, CLIENT_GROUP_TO_IDS, VALID_BUSINESSES, VALID_SUBBUSINESSES
from agent.llm_client import get_llm_client
from agent.config import DATE_PARSER_MODEL

# --- Canonical Values and Mappings ---

CANONICAL_REGIONS = ["AMERICAS", "EMEA", "ASIA", "NA"]
REGION_ALIAS_MAP = {
    "americas": "AMERICAS",
    "america": "AMERICAS",
    "emea": "EMEA",
    "europe": "EMEA",
    "asia": "ASIA",
    "na": "NA",
    "north america": "NA"
}

CANONICAL_COUNTRIES = ["USA", "CAN", "BRA", "GBR", "FRA", "DEU", "JPN", "HKG", "AUS"]
COUNTRY_ALIAS_MAP = {
    "united states": "USA",
    "us": "USA",
    "usa": "USA",
    "canada": "CAN",
    "brazil": "BRA",
    "united kingdom": "GBR",
    "uk": "GBR",
    "france": "FRA",
    "germany": "DEU",
    "japan": "JPN",
    "hong kong": "HKG",
    "australia": "AUS"
}

# --- Entity Resolvers ---

def resolve_regions(names: List[str]) -> List[str]:
    """
    Resolves a list of region names/aliases into a list of canonical region names.
    Handles 'global' to return all regions.
    """
    if not names:
        return []

    resolved_regions: Set[str] = set()
    
    # Standardize input to lower case for matching
    clean_names = [name.lower().strip() for name in names]

    if "global" in clean_names:
        return CANONICAL_REGIONS

    for name in clean_names:
        if name in REGION_ALIAS_MAP:
            resolved_regions.add(REGION_ALIAS_MAP[name])
        else:
            print(f"Warning: Could not resolve region '{name}'. Ignoring.")
    
    return list(resolved_regions)


def resolve_clients(names: List[str]) -> List[str]:
    """
    Resolves a list of client or group names into a list of client IDs.

    - Handles fuzzy matching for typos using RapidFuzz.
    - Expands group names into their constituent client IDs.
    - Deduplicates the final list of IDs.
    """
    if not names:
        return []

    # Combine all known client and group names for efficient matching
    all_known_entities = list(CLIENT_NAME_TO_ID.keys()) + list(CLIENT_GROUP_TO_IDS.keys())
    resolved_ids: Set[str] = set()

    for name in names:
        # Standardize the input name
        clean_name = name.lower().strip()

        # Find the best match from our knowledge base using RapidFuzz
        # process.extractOne returns (match, score, key)
        best_match, score, _ = process.extractOne(clean_name, all_known_entities)
        
        # We can tune this threshold (0-100 for RapidFuzz)
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


def resolve_sub_businesses(names: List[str]) -> List[str]:
    """
    Resolves a list of sub-business names into a list of valid sub-business names.
    """
    if not names:
        return []
        
    resolved_names: Set[str] = set()
    for name in names:
        clean_name = name.lower().strip()
        match, score, _ = process.extractOne(clean_name, VALID_SUBBUSINESSES)
        if score > 80:
            resolved_names.add(match)
            
    return list(resolved_names)


# --- Date Resolution ---

class DateRange(BaseModel):
    start_date: str = Field(..., description="The start date in YYYY-MM-DD format.")
    end_date: str = Field(..., description="The end date in YYYY-MM-DD format.")

def _get_llm_date_range(date_description: str) -> (str, str):
    """(Internal) Use an LLM to parse a complex date description."""
    client = get_llm_client()
    
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
            model=DATE_PARSER_MODEL,
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"}
        )
        response_json = json.loads(response.choices[0].message.content)
        date_range = DateRange.model_validate(response_json)
        return date_range.start_date, date_range.end_date
    except Exception as e:
        print(f"--- LLM Date Parsing failed: {e}. Raising exception. ---")
        raise

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
        start_date = datetime(year - 1, 10, 1).strftime('%Y-%m-%d')
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
        # This is not an error, just means it's not a simple date.
        pass

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


# --- Knowledge Base Accessor ---

def get_valid_business_lines():
    """
    Returns a dictionary of valid business and sub-business lines.
    This is used to provide the planner with up-to-date knowledge.
    """
    return {
        "valid_businesses": VALID_BUSINESSES,
        "valid_subbusinesses": VALID_SUBBUSINESSES
    } 

def resolve_countries(names: List[str]) -> List[str]:
    """
    Resolves a list of country names/aliases into a list of canonical country codes.
    """
    if not names:
        return []

    resolved_countries: Set[str] = set()
    clean_names = [name.lower().strip() for name in names]

    for name in clean_names:
        if name in COUNTRY_ALIAS_MAP:
            resolved_countries.add(COUNTRY_ALIAS_MAP[name])
        else:
            print(f"Warning: Could not resolve country '{name}'. Ignoring.")
            
    return list(resolved_countries) 