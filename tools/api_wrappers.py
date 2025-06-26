import pandas as pd
import numpy as np
from typing import List, Literal, Optional

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
    granularity: Optional[str] = "aggregate"
) -> pd.DataFrame:
    """
    Generates a DataFrame of daily data, then filters and aggregates it based on the provided parameters.
    This function simulates a real-world API that performs filtering and aggregation on the server side.
    
    balance_type filtering rules:
    - PB/Clearing subbusiness: "Debit", "Credit", "Physical Shorts"
    - SPG subbusiness: "Synthetic Longs", "Synthetic Shorts"
    - Invalid combinations return empty DataFrame
    """
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

    # 3. --- Aggregate Data ---
    if granularity == "aggregate":
        total = df[metric].sum() if metric == 'revenues' else df[metric].mean()
        return pd.DataFrame({metric: [total]})
    
    # Special handling for date granularity to ensure proper time series structure
    if granularity == "date":
        # For time series, we want to group by date and potentially other dimensions
        # This ensures we get proper time series data even with multiple clients
        if len(df['client_id'].unique()) > 1:
            # Multiple clients - aggregate by date and preserve client info
            agg_func = 'sum' if metric == 'revenues' else 'mean'
            agg_df = df.groupby(['date', 'client_id'])[metric].agg(agg_func).reset_index()
            # Add client name for better plotting
            agg_df['client_name'] = agg_df['client_id'].apply(lambda x: x.replace('cl_id_', '').title())
        else:
            # Single client - just group by date
            agg_func = 'sum' if metric == 'revenues' else 'mean'
            agg_df = df.groupby('date')[metric].agg(agg_func).reset_index()
        return agg_df
    
    # Standard aggregation for other granularities
    group_col = 'client_id' if granularity == 'client' else granularity
    if group_col not in df.columns:
        return pd.DataFrame()

    agg_func = 'sum' if metric == 'revenues' else 'mean'
    agg_df = df.groupby(group_col)[metric].agg(agg_func).reset_index()
    
    # Add client names for better display
    if granularity == 'client':
        agg_df['client_name'] = agg_df['client_id'].apply(lambda x: x.replace('cl_id_', '').title())
    
    return agg_df

def _generate_mock_capital_data(
    start_date: str, 
    end_date: str,
    metric: str = "Total AE",
    client_ids: Optional[List[str]] = None,
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC", "Equities"]] = None,
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None,
    granularity: Optional[str] = "aggregate"
) -> pd.DataFrame:
    """
    Generates a DataFrame of daily capital data for the specified metric.
    Supports: "Total RWA", "Portfolio RWA", "Borrow RWA", "Balance Sheet", 
    "Supplemental Balance Sheet", "GSIB Points", "Total AE", "Preferred AE".
    Capital metrics only support filtering by subbusiness, not by region or country.
    """
    # 1. --- Generate Base Data ---
    dates = pd.to_datetime(pd.date_range(start_date, end_date, freq='D'))
    base_client_list = client_ids if client_ids else [f"cl_id_{i}" for i in range(5)]
    
    businesses = ["Prime", "Equities Ex Prime", "FICC"]
    subbusinesses = ["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]

    data = []
    if not base_client_list: 
        base_client_list = [f"cl_id_{i}" for i in range(5)]

    for date in dates:
        for client_id in base_client_list:
            for _ in range(np.random.randint(1, 4)): # Each client has a few random business lines each day
                # Generate different value ranges based on metric type
                if "RWA" in metric:
                    # RWA values are typically larger than AE
                    value = np.random.randint(100000, 5000000)
                elif metric in ["Balance Sheet", "Supplemental Balance Sheet"]:
                    # Balance sheet values are typically very large
                    value = np.random.randint(1000000, 20000000)
                elif "AE" in metric or "Equity" in metric:
                    # Attributed Equity values
                    value = np.random.randint(50000, 2000000)
                elif "GSIB" in metric:
                    # GSIB Points are typically smaller numbers
                    value = np.random.randint(10, 1000)
                else:
                    # Default capital values
                    value = np.random.randint(50000, 2000000)
                
                data.append({
                    "date": date, 
                    "client_id": client_id, 
                    "business": np.random.choice(businesses),
                    "subbusiness": np.random.choice(subbusinesses), 
                    metric: value
                })

    if not data:
        return pd.DataFrame() 
    
    df = pd.DataFrame(data)

    # 2. --- Apply Filters ---
    # Note: Capital only supports client, business, and subbusiness filtering (no region/country)
    if client_ids:
        df = df[df['client_id'].isin(client_ids)]
    if business:
        if business == "Equities":
            df = df[df['business'].isin(["Prime", "Equities Ex Prime"])]
        else:
            df = df[df['business'] == business]
    if subbusiness:
        df = df[df['subbusiness'] == subbusiness]

    if df.empty:
        return pd.DataFrame()

    # 3. --- Aggregate Data ---
    if granularity == "aggregate":
        total = df[metric].sum()
        return pd.DataFrame({metric: [total]})
    
    # Special handling for date granularity
    if granularity == "date":
        if len(df['client_id'].unique()) > 1:
            agg_df = df.groupby(['date', 'client_id'])[metric].sum().reset_index()
            agg_df['client_name'] = agg_df['client_id'].apply(lambda x: x.replace('cl_id_', '').title())
        else:
            agg_df = df.groupby('date')[metric].sum().reset_index()
        return agg_df
    
    # Standard aggregation for other granularities
    group_col = 'client_id' if granularity == 'client' else granularity
    if group_col not in df.columns:
        return pd.DataFrame()

    agg_df = df.groupby(group_col)[metric].sum().reset_index()
    
    # Add client names for better display
    if granularity == 'client':
        agg_df['client_name'] = agg_df['client_id'].apply(lambda x: x.replace('cl_id_', '').title())
    
    return agg_df

# --- API Wrappers ---

def get_revenues(
    client_ids: List[str],
    start_date: str,
    end_date: str,
    granularity: Literal["aggregate", "client", "date", "business", "subbusiness", "region", "fin_or_exec", "primary_or_secondary"],
    region: Optional[List[str]] = None,
    fin_or_exec: Optional[List[str]] = None,
    primary_or_secondary: Optional[List[str]] = None,
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC", "Equities"]] = None,
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None,
) -> pd.DataFrame:
    """
    Placeholder for the get_revenues API.
    Returns a pandas DataFrame of revenue data, aggregated as specified.
    """
    print(f"--- CALLING get_revenues(client_ids={client_ids}, start_date='{start_date}', end_date='{end_date}', business='{business}', subbusiness='{subbusiness}', granularity='{granularity}') ---")
    
    return _generate_mock_data(
        start_date=start_date, end_date=end_date, metric="revenues",
        client_ids=client_ids, region=region, fin_or_exec=fin_or_exec,
        primary_or_secondary=primary_or_secondary, business=business,
        subbusiness=subbusiness, granularity=granularity
    )

def get_balances(
    client_ids: List[str],
    start_date: str,
    end_date: str,
    granularity: Literal["aggregate", "client", "date", "business", "subbusiness", "region", "country", "balance_type"],
    region: Optional[List[str]] = None,
    country: Optional[List[str]] = None,
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC", "Equities"]] = None,
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None,
    balance_type: Optional[Literal["Debit", "Credit", "Physical Shorts", "Synthetic Longs", "Synthetic Shorts"]] = None,
) -> pd.DataFrame:
    """
    Placeholder for the get_balances API.
    Returns a pandas DataFrame of balance data, aggregated as specified.
    
    balance_type parameter supports:
    - PB/Clearing subbusiness: "Debit", "Credit", "Physical Shorts"
    - SPG subbusiness: "Synthetic Longs", "Synthetic Shorts"
    """
    print(f"--- CALLING get_balances(client_ids={client_ids}, start_date='{start_date}', end_date='{end_date}', business='{business}', subbusiness='{subbusiness}', balance_type='{balance_type}', granularity='{granularity}') ---")

    return _generate_mock_data(
        start_date=start_date, end_date=end_date, metric="balances",
        client_ids=client_ids, region=region, country=country,
        business=business, subbusiness=subbusiness, balance_type=balance_type, granularity=granularity
    )

def get_capital(
    client_ids: List[str],
    start_date: str,
    end_date: str,
    granularity: Literal["aggregate", "client", "date", "business", "subbusiness"],
    metric: str = "Total AE",
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC", "Equities"]] = None,
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None,
) -> pd.DataFrame:
    """
    Placeholder for the get_capital API.
    Returns a pandas DataFrame of capital data, aggregated as specified.
    Supports multiple metrics: "Total RWA", "Portfolio RWA", "Borrow RWA", "Balance Sheet", 
    "Supplemental Balance Sheet", "GSIB Points", "Total AE", "Preferred AE".
    Note: Capital data only supports filtering by subbusiness, not by region or country.
    """
    print(f"--- CALLING get_capital(client_ids={client_ids}, start_date='{start_date}', end_date='{end_date}', metric='{metric}', business='{business}', subbusiness='{subbusiness}', granularity='{granularity}') ---")

    return _generate_mock_capital_data(
        start_date=start_date, end_date=end_date, metric=metric,
        client_ids=client_ids, business=business,
        subbusiness=subbusiness, granularity=granularity
    )

def get_balances_decomposition(
    client_ids: List[str],
    start_date: str,
    end_date: str,
    granularity: Literal["aggregate", "client", "business", "subbusiness", "region", "country"],
    region: Optional[List[str]] = None,
    country: Optional[List[str]] = None,
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC", "Equities"]] = None,
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None,
) -> pd.DataFrame:
    """
    Placeholder for the get_balances_decomposition API.
    Returns a DataFrame breaking down balance changes into MTM and Activity components.
    """
    print(f"--- CALLING get_balances_decomposition(client_ids={client_ids}, start_date='{start_date}', end_date='{end_date}', granularity='{granularity}') ---")

    # This is a simplified mock. A real implementation would fetch data and calculate the decomposition.
    base_data = _generate_mock_data(
        start_date=start_date, end_date=end_date, metric="balances",
        client_ids=client_ids, region=region, country=country,
        business=business, subbusiness=subbusiness, granularity=granularity
    )

    if base_data.empty:
        return pd.DataFrame(columns=[granularity, 'Balance.Start', 'Balance.End', 'Balance.Delta.Total', 'Balance.Delta.MTM', 'Balance.Delta.Activity'])

    # Mock the decomposition columns
    # In a real scenario, these would be calculated based on a more complex dataset
    if 'balances' in base_data.columns:
        base_data = base_data.rename(columns={'balances': 'Balance.End'})
        base_data['Balance.Start'] = base_data['Balance.End'] * (1 + np.random.uniform(-0.2, 0.2, size=len(base_data)))
    else:
         # Handle aggregate case where only one value exists
        base_data['Balance.End'] = base_data.iloc[:, 0]
        base_data['Balance.Start'] = base_data['Balance.End'] * (1 + np.random.uniform(-0.2, 0.2, size=len(base_data)))


    base_data['Balance.Delta.Total'] = base_data['Balance.End'] - base_data['Balance.Start']
    base_data['Balance.Delta.MTM'] = base_data['Balance.Delta.Total'] * np.random.uniform(0.3, 0.7, size=len(base_data))
    base_data['Balance.Delta.Activity'] = base_data['Balance.Delta.Total'] - base_data['Balance.Delta.MTM']
    
    return base_data 