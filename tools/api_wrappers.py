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
    granularity: Optional[str] = "aggregate"
) -> pd.DataFrame:
    """
    Generates a DataFrame of daily data, then filters and aggregates it based on the provided parameters.
    This function simulates a real-world API that performs filtering and aggregation on the server side.
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
                data.append({
                    "date": date, "client_id": client_id, "business": np.random.choice(businesses),
                    "subbusiness": np.random.choice(subbusinesses), "region": np.random.choice(regions),
                    "country": np.random.choice(country_map.get(np.random.choice(regions), ["USA"])),
                    "fin_or_exec": np.random.choice(fin_or_exec_options),
                    "primary_or_secondary": np.random.choice(primary_or_secondary_options),
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

    if df.empty:
        return pd.DataFrame()

    # 3. --- Aggregate Data ---
    if granularity == "aggregate":
        total = df[metric].sum() if metric == 'revenues' else df[metric].mean()
        return pd.DataFrame({metric: [total]})
    
    group_col = 'client_id' if granularity == 'client' else granularity
    if group_col not in df.columns:
        return pd.DataFrame()

    agg_func = 'sum' if metric == 'revenues' else 'mean'
    agg_df = df.groupby(group_col)[metric].agg(agg_func).reset_index()
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
    granularity: Literal["aggregate", "client", "date", "business", "subbusiness", "region", "country"],
    region: Optional[List[str]] = None,
    country: Optional[List[str]] = None,
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC", "Equities"]] = None,
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None,
) -> pd.DataFrame:
    """
    Placeholder for the get_balances API.
    Returns a pandas DataFrame of balance data, aggregated as specified.
    """
    print(f"--- CALLING get_balances(client_ids={client_ids}, start_date='{start_date}', end_date='{end_date}', business='{business}', subbusiness='{subbusiness}', granularity='{granularity}') ---")

    return _generate_mock_data(
        start_date=start_date, end_date=end_date, metric="balances",
        client_ids=client_ids, region=region, country=country,
        business=business, subbusiness=subbusiness, granularity=granularity
    ) 