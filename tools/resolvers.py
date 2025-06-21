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

# New imports for vector-based resolution
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from knowledge_base.client_data import CLIENT_NAME_TO_ID, CLIENT_GROUP_TO_IDS, VALID_BUSINESSES, VALID_SUBBUSINESSES

# --- Helper class for Vector-based Entity Resolution ---

class VectorResolver:
    """
    A generic resolver that uses vector embeddings and FAISS for fast and
    accurate semantic matching of entities.
    """
    def __init__(self, items_to_index: List[str], model_name: str = 'BAAI/bge-base-en-v1.5'):
        print(f"Initializing VectorResolver with {len(items_to_index)} items...")
        self.model = SentenceTransformer(model_name)
        self.items = items_to_index
        
        # Generate embeddings and build the FAISS index
        embeddings = self.model.encode(self.items, convert_to_tensor=False, show_progress_bar=False)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(np.array(embeddings, dtype=np.float32))
        print("VectorResolver initialized successfully.")

    def find_best_match(self, query: str, score_threshold: float = 0.6) -> str | None:
        """
        Finds the best match for a given query string from the indexed items.

        Args:
            query: The string to match.
            score_threshold: The minimum similarity score to consider a match valid.
                             This is based on cosine similarity, so it's between -1 and 1.
                             A value of 0.6 is a reasonable starting point.

        Returns:
            The best matching string from the list, or None if no match is found
            above the threshold.
        """
        if not query:
            return None
            
        query_embedding = self.model.encode([query], convert_to_tensor=False)
        # FAISS returns distances (L2), not similarity. For normalized embeddings (like from SBERT),
        # L2 distance `d` can be converted to cosine similarity `s` via `s = 1 - (d^2 / 2)`.
        distances, indices = self.index.search(np.array(query_embedding, dtype=np.float32), 1)
        
        best_match_index = indices[0][0]
        best_match_distance = distances[0][0]
        
        # Convert L2 distance to cosine similarity
        cosine_similarity = 1 - (best_match_distance**2 / 2)

        if cosine_similarity >= score_threshold:
            return self.items[best_match_index]
        else:
            print(f"Warning: Match for '{query}' found ('{self.items[best_match_index]}'), but score {cosine_similarity:.2f} is below threshold {score_threshold}. Ignoring.")
            return None

# --- Main Resolver Classes ---

class ClientNameResolver:
    """
    Resolves client names and group names from natural language
    into lists of specific client IDs using a vector-based approach.
    """
    def __init__(self):
        # Prepare lists for indexing
        self.client_name_to_id = {name.lower(): id for name, id in CLIENT_NAME_TO_ID.items()}
        self.client_group_to_ids = {group.lower(): ids for group, ids in CLIENT_GROUP_TO_IDS.items()}
        
        # All individual client names that can be matched against
        self.individual_client_names = list(self.client_name_to_id.keys())
        
        # Instantiate the vector resolver for individual names
        self.vector_resolver = VectorResolver(self.individual_client_names)

    def resolve(self, names: List[str]) -> List[str]:
        """
        Resolves a list of client or group names into a list of client IDs.
        - Handles semantic matching for individual client names.
        - Expands group names into their constituent client IDs.
        - Deduplicates the final list of IDs.
        """
        if not names:
            return []

        resolved_ids: Set[str] = set()

        for name in names:
            clean_name = name.lower().strip()

            # First, check for an exact match in groups (e.g., "Top 5 Clients")
            if clean_name in self.client_group_to_ids:
                resolved_ids.update(self.client_group_to_ids[clean_name])
                continue

            # If not a group, find the best semantic match for an individual client
            best_match = self.vector_resolver.find_best_match(clean_name)
            
            if best_match:
                # Get the ID for the matched name
                resolved_ids.add(self.client_name_to_id[best_match])

        return list(resolved_ids)


def resolve_sub_businesses(names: List[str]) -> List[str]:
    """
    Resolves a list of sub-business names into a list of valid sub-business names.
    """
    if not names:
        return []
        
    resolver = VectorResolver(VALID_SUBBUSINESSES)
    
    resolved_names: Set[str] = set()
    for name in names:
        match = resolver.find_best_match(name.lower().strip())
        if match:
            resolved_names.add(match)
            
    return list(resolved_names)


# --- Date Resolution (Largely Unchanged) ---

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
            model="gpt-3.5-turbo",
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