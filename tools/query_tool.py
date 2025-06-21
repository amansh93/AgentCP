from typing import List, Literal, Optional
import pandas as pd
from pydantic import BaseModel, Field

from .resolvers import resolve_clients, resolve_dates
from .api_wrappers import get_revenues, get_balances

class SimpleQueryInput(BaseModel):
    """
    Defines the structured input required by the SimpleQueryTool.
    This model serves as a contract for the Planner.
    """
    metric: Literal["revenues", "balances"]
    entities: List[str] = Field(..., description="List of client names or group names, e.g., ['millennium', 'systematic']")
    date_description: str = Field(..., description="A natural language description of the date range, e.g., 'Q1 2024'")
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC"]] = None
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None
    granularity: Literal["aggregate", "client", "date"]

class SimpleQueryTool:
    """
    A tool to execute simple, single-API queries.
    It orchestrates resolvers and API wrappers to fulfill a structured request.
    """

    def execute(self, query_input: SimpleQueryInput) -> pd.DataFrame:
        """
        Takes a structured query object, resolves entities, and calls the correct API.
        """
        print("\n--- Executing SimpleQueryTool ---")
        
        # 1. Resolve entities using our robust resolvers
        client_ids = resolve_clients(query_input.entities)
        start_date, end_date = resolve_dates(query_input.date_description)

        print(f"Resolved Clients: {client_ids}")
        print(f"Resolved Dates: {start_date} to {end_date}")

        # 2. Select the correct API function based on the metric
        api_call = get_revenues if query_input.metric == "revenues" else get_balances

        # 3. Call the selected API with the resolved and validated parameters
        result_df = api_call(
            client_ids=client_ids,
            start_date=start_date,
            end_date=end_date,
            granularity=query_input.granularity,
            business=query_input.business,
            subbusiness=query_input.subbusiness
        )
        
        print("--- SimpleQueryTool Execution Finished ---")
        return result_df 