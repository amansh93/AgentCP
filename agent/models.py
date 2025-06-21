from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Union

# --- Parameter models for each available tool ---

class DataFetchParameters(BaseModel):
    """Parameters for fetching data from our APIs."""
    metric: Literal["revenues", "balances"]
    entities: List[str]
    date_description: str
    granularity: Literal["aggregate", "client", "date", "business", "subbusiness", "region", "country"]
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC"]] = None
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None
    region: Optional[List[str]] = Field(None, description="A list of regions to filter on, e.g., ['EMEA', 'AMERICAS']")
    country: Optional[List[str]] = Field(None, description="A list of countries to filter on (for balances metric ONLY).")
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

# A single step in a plan can be any of these types
PlanStep = Union[DataFetchStep, DescribeDataframeStep, CodeExecutorStep, GetValidBusinessLinesStep]

# The final plan is a list of these steps
class MultiStepPlan(BaseModel):
    plan: List[PlanStep] 