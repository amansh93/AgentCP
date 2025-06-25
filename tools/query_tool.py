from typing import List, Literal, Optional, Any
import pandas as pd
from pydantic import BaseModel, Field, validator

from .resolvers import resolve_clients, resolve_dates, resolve_regions, resolve_countries, resolve_fin_or_exec, resolve_primary_or_secondary
from .api_wrappers import get_revenues, get_balances, get_balances_decomposition, get_capital

class InformUserInput(BaseModel):
    """Input model for the InformUserTool."""
    message: str = Field(..., description="The message to convey to the user.")

class InformUserTool:
    """A tool to communicate information or limitations back to the user."""
    def execute(self, tool_input: InformUserInput) -> str:
        """Simply returns the message to be shown to the user."""
        print(f"\n--- Informing User: {tool_input.message} ---")
        return tool_input.message

class SimpleQueryInput(BaseModel):
    """
    Defines the structured input required by the SimpleQueryTool.
    This model serves as a contract for the Planner.
    """
    metric: Literal["revenues", "balances", "balances_decomposition", "Total RWA", "Portfolio RWA", "Borrow RWA", "Balance Sheet", "Supplemental Balance Sheet", "GSIB Points", "Total AE", "Preferred AE"]
    entities: List[str] = Field(..., description="List of client names or group names, e.g., ['millennium', 'systematic']")
    date_description: str = Field(..., description="A natural language description of the date range, e.g., 'Q1 2024'")
    regions: Optional[List[str]] = Field(None, description="A list of regions or aliases to filter on, e.g., ['Europe', 'AMERICAS', 'global']")
    countries: Optional[List[str]] = Field(None, alias="country", description="A list of countries or aliases to filter on (for balances only), e.g., ['UK', 'United States']")
    fin_or_exec: Optional[List[str]] = Field(None, description="Filter for financing or execution revenues (for revenues metric ONLY). Aliases: 'commissions', 'comms'.")
    primary_or_secondary: Optional[List[str]] = Field(None, description="Filter for primary or secondary revenues (for revenues metric ONLY).")
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC", "Equities"]] = None
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None
    granularity: Literal["aggregate", "client", "date", "business", "subbusiness", "region", "country", "fin_or_exec", "primary_or_secondary"]

    @validator('business', 'subbusiness', pre=True)
    def empty_str_to_none(cls, v: Any) -> Optional[Any]:
        """Converts an explicit 'None' string from the LLM to a real None."""
        if isinstance(v, str) and v.lower() == 'none':
            return None
        return v

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
        regions = resolve_regions(query_input.regions)
        countries = resolve_countries(query_input.countries)
        fin_or_exec = resolve_fin_or_exec(query_input.fin_or_exec)
        primary_or_secondary = resolve_primary_or_secondary(query_input.primary_or_secondary)

        print(f"Resolved Clients: {client_ids}")
        print(f"Resolved Dates: {start_date} to {end_date}")
        print(f"Resolved Regions: {regions}")
        print(f"Resolved Countries: {countries}")
        print(f"Resolved Fin/Exec: {fin_or_exec}")
        print(f"Resolved Primary/Secondary: {primary_or_secondary}")

        # 2. Select the correct API function based on the metric
        if query_input.metric == "revenues":
            result_df = get_revenues(
                client_ids=client_ids,
                start_date=start_date,
                end_date=end_date,
                granularity=query_input.granularity,
                region=regions,
                fin_or_exec=fin_or_exec,
                primary_or_secondary=primary_or_secondary,
                business=query_input.business,
                subbusiness=query_input.subbusiness
            )
        elif query_input.metric == "balances_decomposition":
            result_df = get_balances_decomposition(
                client_ids=client_ids,
                start_date=start_date,
                end_date=end_date,
                granularity=query_input.granularity,
                region=regions,
                country=countries,
                business=query_input.business,
                subbusiness=query_input.subbusiness
            )
        elif query_input.metric in ["Total RWA", "Portfolio RWA", "Borrow RWA", "Balance Sheet", "Supplemental Balance Sheet", "GSIB Points", "Total AE", "Preferred AE"]:
            result_df = get_capital(
                client_ids=client_ids,
                start_date=start_date,
                end_date=end_date,
                granularity=query_input.granularity,
                metric=query_input.metric,
                business=query_input.business,
                subbusiness=query_input.subbusiness
            )
        else: # metric is "balances"
            result_df = get_balances(
                client_ids=client_ids,
                start_date=start_date,
                end_date=end_date,
                granularity=query_input.granularity,
                region=regions,
                country=countries,
                business=query_input.business,
                subbusiness=query_input.subbusiness
            )
        
        print("--- SimpleQueryTool Execution Finished ---")
        return result_df 