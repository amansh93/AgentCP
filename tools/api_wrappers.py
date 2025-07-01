import pandas as pd
import numpy as np
from typing import List, Literal, Optional
from datetime import datetime, timedelta
import re

# --- Main Data Generation & Filtering Function ---

def _generate_mock_data(
    start_date: str, 
    end_date: str,
    metric: Literal["revenues", "balances"],
    client_ids: Optional[List[str]] = None,
    region: Optional[List[str]] = None,
    country: Optional[List[str]] = None,
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC", "Equities"]] = None,
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None,
    fin_or_exec: Optional[List[str]] = None,
    primary_or_secondary: Optional[List[str]] = None,
    balance_type: Optional[Literal["Debit", "Credit", "Physical Shorts", "Synthetic Longs", "Synthetic Shorts"]] = None,
    row_granularity: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Generates a DataFrame of daily data, then filters and aggregates it based on the provided parameters.
    This function simulates a real-world API that performs filtering and aggregation on the server side.
    
    row_granularity now accepts a list of up to 2 dimensions for multi-dimensional grouping.
    
    balance_type filtering rules:
    - PB/Clearing subbusiness: "Debit", "Credit", "Physical Shorts"
    - SPG subbusiness: "Synthetic Longs", "Synthetic Shorts"
    - Invalid combinations return empty DataFrame
    """
    if row_granularity is None:
        row_granularity = ["aggregate"]
        
    # 1. --- Generate Base Data ---
    dates = pd.to_datetime(pd.date_range(start_date, end_date, freq='D'))
    base_client_list = client_ids if client_ids else [f"cl_id_{i}" for i in range(5)]
    
    businesses = ["Prime", "Equities Ex Prime", "FICC"]
    subbusinesses = ["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]
    regions = ["AMERICAS", "EMEA", "ASIA", "NA"]
    country_map = {
        "AMERICAS": ["USA", "CAN", "BRA"],
        "EMEA": ["GBR", "FRA", "DEU"],
        "ASIA": ["JPN", "HKG", "AUS"],
        "NA": ["USA", "CAN"]
    }
    fin_or_exec_options = ["Financing", "Execution"]
    primary_or_secondary_options = ["Primary", "Secondary"]

    data = []
    if not base_client_list: # Ensure data is generated if no clients are specified
        base_client_list = [f"cl_id_{i}" for i in range(5)]

    for date in dates:
        for client_id in base_client_list:
            for _ in range(np.random.randint(1, 4)): # Each client has a few random business lines each day
                chosen_subbusiness = np.random.choice(subbusinesses)
                chosen_region = np.random.choice(regions)
                
                # Generate appropriate balance_type based on subbusiness
                if chosen_subbusiness in ["PB", "Clearing"]:
                    balance_type_options = ["Debit", "Credit", "Physical Shorts"]
                elif chosen_subbusiness == "SPG":
                    balance_type_options = ["Synthetic Longs", "Synthetic Shorts"]
                else:
                    # For other subbusinesses, use PB-style balance types as default
                    balance_type_options = ["Debit", "Credit", "Physical Shorts"]
                
                data.append({
                    "date": date, "client_id": client_id, "business": np.random.choice(businesses),
                    "subbusiness": chosen_subbusiness, "region": chosen_region,
                    "country": np.random.choice(country_map.get(chosen_region, ["USA"])),
                    "fin_or_exec": np.random.choice(fin_or_exec_options),
                    "primary_or_secondary": np.random.choice(primary_or_secondary_options),
                    "balance_type": np.random.choice(balance_type_options),
                    "revenues": np.random.randint(1000, 50000), "balances": np.random.randint(100000, 5000000)
                })

    if not data:
        return pd.DataFrame() # Return empty frame if no data was generated
    
    df = pd.DataFrame(data)

    # 2. --- Apply Filters ---
    if client_ids: # Note: This check is different from the one for base_client_list
        df = df[df['client_id'].isin(client_ids)]
    if region:
        df = df[df['region'].isin(region)]
    if country:
        df = df[df['country'].isin(country)]
    if fin_or_exec:
        df = df[df['fin_or_exec'].isin(fin_or_exec)]
    if primary_or_secondary:
        df = df[df['primary_or_secondary'].isin(primary_or_secondary)]
    if business:
        if business == "Equities":
            df = df[df['business'].isin(["Prime", "Equities Ex Prime"])]
        else:
            df = df[df['business'] == business]
    if subbusiness:
        df = df[df['subbusiness'] == subbusiness]
    
    # Apply balance_type filter with validation
    if balance_type:
        # First validate that balance_type is compatible with subbusiness
        if not df.empty:
            unique_subbusinesses = df['subbusiness'].unique()
            
            # Check for invalid combinations and return empty DataFrame if found
            for sb in unique_subbusinesses:
                if sb in ["PB", "Clearing"] and balance_type not in ["Debit", "Credit", "Physical Shorts"]:
                    return pd.DataFrame()  # Invalid combination
                elif sb == "SPG" and balance_type not in ["Synthetic Longs", "Synthetic Shorts"]:
                    return pd.DataFrame()  # Invalid combination
        
        # Apply the filter if validation passes
        df = df[df['balance_type'] == balance_type]

    if df.empty:
        return pd.DataFrame()

    # 3. --- Aggregate Data Based on Row Granularity ---
    if "aggregate" in row_granularity:
        total = df[metric].sum() if metric == 'revenues' else df[metric].mean()
        return pd.DataFrame({metric: [total]})
    
    # Map granularity values to actual column names
    granularity_column_map = {
        "client": "client_id",
        "date": "date",
        "business": "business",
        "subbusiness": "subbusiness",
        "region": "region",
        "country": "country",
        "balance_type": "balance_type",
        "fin_or_exec": "fin_or_exec",
        "primary_or_secondary": "primary_or_secondary"
    }
    
    # Build group columns from row_granularity
    group_cols = []
    for granularity in row_granularity:
        if granularity in granularity_column_map:
            col_name = granularity_column_map[granularity]
            if col_name in df.columns:
                group_cols.append(col_name)
    
    if not group_cols:
        return pd.DataFrame()

    # Special handling for date granularity to ensure proper time series structure
    if "date" in row_granularity:
        # For time series, we want to handle multiple clients properly
        agg_func = 'sum' if metric == 'revenues' else 'mean'
        
        if len(df['client_id'].unique()) > 1 and "client_id" not in group_cols:
            # Multiple clients but client not in grouping - add client to preserve structure
            group_cols_with_client = group_cols + ["client_id"]
            agg_df = df.groupby(group_cols_with_client)[metric].agg(agg_func).reset_index()
            # Add client name for better plotting
            agg_df['client_name'] = agg_df['client_id'].apply(lambda x: x.replace('cl_id_', '').title())
        else:
            # Standard grouping
            agg_df = df.groupby(group_cols)[metric].agg(agg_func).reset_index()
        return agg_df
    
    # Standard aggregation for non-date granularities
    agg_func = 'sum' if metric == 'revenues' else 'mean'
    agg_df = df.groupby(group_cols)[metric].agg(agg_func).reset_index()
    
    # Add client names for better display if client is in the grouping
    if 'client_id' in group_cols:
        agg_df['client_name'] = agg_df['client_id'].apply(lambda x: x.replace('cl_id_', '').title())
    
    return agg_df

# --- API Wrappers ---

def get_revenues(
    entities: List[str],
    date_range: str,
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC", "Equities"]] = None,
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None,
    regions: Optional[List[str]] = None,
    fin_or_exec: Optional[List[str]] = None,
    primary_or_secondary: Optional[List[str]] = None,
    row_granularity: List[str] = ["aggregate"],
    col_granularity: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Retrieves revenue data for specific entities and date range.
    Now supports multi-dimensional row_granularity with up to 2 dimensions.
    """
    try:
        start_date, end_date = _parse_date_range(date_range)
        client_ids = [_resolve_client_name(entity) for entity in entities]
        
        mock_df = _generate_mock_data(
            start_date, end_date, "revenues", client_ids, regions, None, business, subbusiness, 
            fin_or_exec, primary_or_secondary, None, row_granularity
        )
        
        # Apply column granularity if specified
        if col_granularity and not mock_df.empty:
            mock_df = _apply_column_granularity(mock_df, col_granularity, "revenues")
        
        return mock_df

    except Exception as e:
        return pd.DataFrame()

def get_balances(
    entities: List[str],
    date_range: str,
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC", "Equities"]] = None,
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None,
    regions: Optional[List[str]] = None,
    countries: Optional[List[str]] = None,
    balance_type: Optional[Literal["Debit", "Credit", "Physical Shorts", "Synthetic Longs", "Synthetic Shorts"]] = None,
    row_granularity: List[str] = ["aggregate"],
    col_granularity: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Retrieves balance data for specific entities and date range.
    Now supports multi-dimensional row_granularity with up to 2 dimensions.
    """
    try:
        start_date, end_date = _parse_date_range(date_range)
        client_ids = [_resolve_client_name(entity) for entity in entities]
        
        mock_df = _generate_mock_data(
            start_date, end_date, "balances", client_ids, regions, countries, business, subbusiness, 
            None, None, balance_type, row_granularity
        )
        
        # Apply column granularity if specified  
        if col_granularity and not mock_df.empty:
            mock_df = _apply_column_granularity(mock_df, col_granularity, "balances")
        
        return mock_df

    except Exception as e:
        return pd.DataFrame()

def get_capital(
    entities: List[str],
    date_range: str,
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC", "Equities"]] = None,
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None,
    regions: Optional[List[str]] = None,
    row_granularity: List[str] = ["aggregate"],
    col_granularity: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Retrieves capital data (Total RWA, Portfolio RWA, etc.) for specific entities and date range.
    Now supports multi-dimensional row_granularity with up to 2 dimensions.
    """
    try:
        start_date, end_date = _parse_date_range(date_range)
        client_ids = [_resolve_client_name(entity) for entity in entities]
        
        # For capital metrics, use balance mock data as a proxy but return different column names
        mock_df = _generate_mock_data(
            start_date, end_date, "balances", client_ids, regions, None, business, subbusiness, 
            None, None, None, row_granularity
        )
        
        if not mock_df.empty and "balances" in mock_df.columns:
            # Transform balance data to capital metrics
            mock_df = mock_df.rename(columns={"balances": "capital"})
            mock_df["capital"] = mock_df["capital"] * 0.1  # Convert to capital ratio
            
            # Apply column granularity if specified
            if col_granularity:
                mock_df = _apply_column_granularity(mock_df, col_granularity, "capital")
        
        return mock_df

    except Exception as e:
        return pd.DataFrame()

def get_balances_decomposition(
    entities: List[str],
    date_range: str,
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC", "Equities"]] = None,
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None,
    regions: Optional[List[str]] = None,
    countries: Optional[List[str]] = None,
    balance_type: Optional[Literal["Debit", "Credit", "Physical Shorts", "Synthetic Longs", "Synthetic Shorts"]] = None,
    row_granularity: List[str] = ["aggregate"]
) -> pd.DataFrame:
    """
    Retrieves detailed balance decomposition data for specific entities and date range.
    Now supports multi-dimensional row_granularity with up to 2 dimensions.
    Note: This function does not support col_granularity (intentionally excluded).
    """
    try:
        start_date, end_date = _parse_date_range(date_range)
        client_ids = [_resolve_client_name(entity) for entity in entities]
        
        mock_df = _generate_mock_data(
            start_date, end_date, "balances", client_ids, regions, countries, business, subbusiness, 
            None, None, balance_type, row_granularity
        )
        
        if not mock_df.empty and "balances" in mock_df.columns:
            # Create decomposition columns
            mock_df = mock_df.rename(columns={"balances": "total_balance"})
            mock_df["cash"] = mock_df["total_balance"] * 0.3
            mock_df["securities"] = mock_df["total_balance"] * 0.5
            mock_df["other"] = mock_df["total_balance"] * 0.2

        return mock_df

    except Exception as e:
        return pd.DataFrame() 

def _parse_date_range(date_description: str) -> tuple[str, str]:
    """
    Parse natural language date description into start_date and end_date.
    This is a simplified version - a real implementation would be more sophisticated.
    """
    # Simple parsing for common patterns
    if "Q1 2024" in date_description:
        return "2024-01-01", "2024-03-31"
    elif "Q2 2024" in date_description:
        return "2024-04-01", "2024-06-30"
    elif "Q3 2024" in date_description:
        return "2024-07-01", "2024-09-30"
    elif "Q4 2024" in date_description:
        return "2024-10-01", "2024-12-31"
    elif "2024" in date_description:
        return "2024-01-01", "2024-12-31"
    elif "last 30 days" in date_description.lower():
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    else:
        # Default to last month
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

def _resolve_client_name(entity: str) -> str:
    """
    Convert entity name to client ID.
    This is a simplified mapping - real implementation would use a lookup service.
    """
    entity_lower = entity.lower()
    if "millennium" in entity_lower:
        return "cl_id_0"
    elif "systematic" in entity_lower:
        return "cl_id_1"
    elif "citadel" in entity_lower:
        return "cl_id_2"
    elif "two sigma" in entity_lower:
        return "cl_id_3"
    elif "bridgewater" in entity_lower:
        return "cl_id_4"
    else:
        # Generate a consistent ID based on the name
        return f"cl_id_{hash(entity) % 100}"

def _apply_column_granularity(df: pd.DataFrame, col_granularity: List[str], metric: str) -> pd.DataFrame:
    """
    Apply column granularity to pivot the data.
    This is a simplified implementation for demonstration.
    """
    if df.empty or not col_granularity:
        return df
    
    # Map granularity values to actual column names
    granularity_column_map = {
        "aggregate": None,  # Special case
        "business": "business",
        "subbusiness": "subbusiness", 
        "region": "region",
        "country": "country",
        "balance_type": "balance_type",
        "fin_or_exec": "fin_or_exec",
        "primary_or_secondary": "primary_or_secondary"
    }
    
    # Handle aggregate case
    if "aggregate" in col_granularity:
        # Sum the metric column
        total = df[metric].sum()
        return pd.DataFrame({f"{metric}_total": [total]})
    
    # Find the column to pivot on
    pivot_col = None
    for granularity in col_granularity:
        if granularity in granularity_column_map and granularity_column_map[granularity]:
            col_name = granularity_column_map[granularity]
            if col_name in df.columns:
                pivot_col = col_name
                break
    
    if not pivot_col:
        return df
    
    try:
        # Create a pivot table
        remaining_cols = [col for col in df.columns if col not in [metric, pivot_col]]
        if remaining_cols:
            pivot_df = df.pivot_table(
                values=metric,
                index=remaining_cols,
                columns=pivot_col,
                aggfunc='sum',
                fill_value=0
            ).reset_index()
            # Flatten column names
            pivot_df.columns.name = None
            return pivot_df
        else:
            # Simple groupby if no other columns
            return df.groupby(pivot_col)[metric].sum().reset_index()
    except Exception:
        # Return original if pivot fails
        return df 