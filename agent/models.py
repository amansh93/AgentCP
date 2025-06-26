from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Union

# --- Parameter models for each available tool ---

class DataFetchParameters(BaseModel):
    """Parameters for fetching data from our APIs."""
    metric: Literal["revenues", "balances", "balances_decomposition", "Total RWA", "Portfolio RWA", "Borrow RWA", "Balance Sheet", "Supplemental Balance Sheet", "GSIB Points", "Total AE", "Preferred AE"]
    entities: List[str]
    date_description: str
    granularity: Literal["aggregate", "client", "date", "business", "subbusiness", "region", "country", "balance_type", "fin_or_exec", "primary_or_secondary"]
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC", "Equities"]] = None
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None
    region: Optional[List[str]] = Field(None, description="A list of regions to filter on, e.g., ['EMEA', 'AMERICAS']")
    country: Optional[List[str]] = Field(None, description="A list of countries to filter on (for balances metric ONLY).")
    balance_type: Optional[Literal["Debit", "Credit", "Physical Shorts", "Synthetic Longs", "Synthetic Shorts"]] = Field(None, description="Filter for balance type (for balances metric ONLY). PB/Clearing supports: Debit, Credit, Physical Shorts. SPG supports: Synthetic Longs, Synthetic Shorts.")
    fin_or_exec: Optional[List[Literal["Financing", "Execution"]]] = Field(None, description="Filter for financing or execution revenues (for revenues metric ONLY).")
    primary_or_secondary: Optional[List[Literal["Primary", "Secondary"]]] = Field(None, description="Filter for primary or secondary revenues (for revenues metric ONLY).")
    output_variable: str = Field(..., description="The variable name to store the resulting dataframe in the workspace.")

class GetValidBusinessLinesParameters(BaseModel):
    """This tool takes no parameters."""
    pass

class DescribeDataframeParameters(BaseModel):
    """Parameters for describing a dataframe that is in the workspace."""
    df_name: str = Field(..., description="The name of the dataframe in the workspace to describe.")

class CodeExecutorParameters(BaseModel):
    """Parameters for executing Python code."""
    code: str = Field(..., description="A string of valid Python code to execute. It has access to a dict called 'dataframes'.")

class InformUserParameters(BaseModel):
    """Parameters for the inform_user tool."""
    message: str = Field(..., description="The message to be sent to the user.")

# --- Step models. 'tool_name' will act as the discriminator ---

class DataFetchStep(BaseModel):
    tool_name: Literal["data_fetch"] = "data_fetch"
    summary: str = Field(..., description="A natural language summary of what this step does for the user.")
    parameters: DataFetchParameters

class GetValidBusinessLinesStep(BaseModel):
    tool_name: Literal["get_valid_business_lines"] = "get_valid_business_lines"
    summary: str = Field(..., description="A natural language summary of what this step does for the user.")
    parameters: GetValidBusinessLinesParameters

class DescribeDataframeStep(BaseModel):
    tool_name: Literal["describe_dataframe"] = "describe_dataframe"
    summary: str = Field(..., description="A natural language summary of what this step does for the user.")
    parameters: DescribeDataframeParameters

class CodeExecutorStep(BaseModel):
    tool_name: Literal["code_executor"] = "code_executor"
    summary: str = Field(..., description="A natural language summary of what this step does for the user.")
    parameters: CodeExecutorParameters

class InformUserStep(BaseModel):
    tool_name: Literal["inform_user"] = "inform_user"
    summary: str = Field(..., description="A natural language summary of what this step does for the user.")
    parameters: InformUserParameters

# A single step in a plan can be any of these types
PlanStep = Union[DataFetchStep, DescribeDataframeStep, CodeExecutorStep, GetValidBusinessLinesStep, InformUserStep]

# The final plan is a list of these steps
class MultiStepPlan(BaseModel):
    plan: List[PlanStep] 