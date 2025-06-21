import pandas as pd
import numpy as np
from typing import List, Literal, Optional

# --- Mock Data Generation ---

def _generate_mock_data(client_ids: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    """Generates a base DataFrame of daily data for specified clients and date range."""
    dates = pd.to_datetime(pd.date_range(start_date, end_date, freq='D'))
    num_clients = len(client_ids) if client_ids else 5
    client_list = client_ids if client_ids else [f"cl_id_{i}" for i in range(num_clients)]
    
    # All possible business/sub-business lines
    businesses = ["Prime", "Equities Ex Prime", "FICC"]
    subbusinesses = ["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]
    regions = ["AMERICAS", "EMEA", "ASIA", "NA"]
    
    # Realistic country mapping
    country_map = {
        "AMERICAS": ["USA", "CAN", "BRA"],
        "EMEA": ["GBR", "FRA", "DEU"],
        "ASIA": ["JPN", "HKG", "AUS"],
        "NA": ["USA", "CAN"] # NA is a subset of AMERICAS for this example
    }

    data = []
    for date in dates:
        for client_id in client_list:
            # Each client has a few random business lines each day
            for _ in range(np.random.randint(1, 4)):
                bus = np.random.choice(businesses)
                sub = np.random.choice(subbusinesses)
                reg = np.random.choice(regions)
                cty = np.random.choice(country_map.get(reg, ["USA"])) # Default to USA if region has no countries
                data.append({
                    "date": date,
                    "client_id": client_id,
                    "business": bus,
                    "subbusiness": sub,
                    "region": reg,
                    "country": cty,
                    "revenues": np.random.randint(1000, 50000),
                    "balances": np.random.randint(100000, 5000000)
                })
    
    if not data:
        return pd.DataFrame(columns=['date', 'client_id', 'business', 'subbusiness', 'region', 'country', 'revenues', 'balances'])

    return pd.DataFrame(data)

# --- API Wrappers ---

def get_revenues(
    client_ids: List[str],
    start_date: str,
    end_date: str,
    granularity: Literal["aggregate", "client", "date", "business", "subbusiness", "region"],
    region: Optional[List[str]] = None,
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC"]] = None,
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None,
) -> pd.DataFrame:
    """
    Placeholder for the get_revenues API.
    Returns a pandas DataFrame of revenue data, aggregated as specified.
    """
    print(f"--- CALLING get_revenues(client_ids={client_ids}, start_date='{start_date}', end_date='{end_date}', business='{business}', subbusiness='{subbusiness}', granularity='{granularity}') ---")

    # Generate a detailed base dataset
    df = _generate_mock_data(client_ids, start_date, end_date)
    if df.empty:
        return pd.DataFrame({'revenues': []})

    # Filter by business lines if specified
    if region:
        df = df[df['region'].isin(region)]
    if business:
        df = df[df['business'] == business]
    if subbusiness:
        df = df[df['subbusiness'] == subbusiness]

    # Group by the specified granularity
    if granularity == "aggregate":
        total_revenues = df['revenues'].sum()
        return pd.DataFrame({"revenues": [total_revenues]})
    
    # For any other granularity, group by that column and sum revenues
    if granularity in ["client", "date", "business", "subbusiness", "region"]:
        # We map granularity to the actual column name
        group_col = 'client_id' if granularity == 'client' else granularity
        
        if group_col not in df.columns:
            return pd.DataFrame({'revenues': []})

        agg_df = df.groupby(group_col)['revenues'].sum().reset_index()
        return agg_df

    # Fallback for safety, though should not be reached with Literal type hint
    return pd.DataFrame({'revenues': []})


def get_balances(
    client_ids: List[str],
    start_date: str,
    end_date: str,
    granularity: Literal["aggregate", "client", "date", "business", "subbusiness", "region", "country"],
    region: Optional[List[str]] = None,
    country: Optional[List[str]] = None,
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC"]] = None,
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None,
) -> pd.DataFrame:
    """
    Placeholder for the get_balances API.
    Returns a pandas DataFrame of balance data, aggregated as specified.
    """
    print(f"--- CALLING get_balances(client_ids={client_ids}, start_date='{start_date}', end_date='{end_date}', business='{business}', subbusiness='{subbusiness}', granularity='{granularity}') ---")

    # Generate a detailed base dataset
    df = _generate_mock_data(client_ids, start_date, end_date)
    if df.empty:
        return pd.DataFrame({'balances': []})

    # Filter by business lines if specified
    if region:
        df = df[df['region'].isin(region)]
    if country:
        df = df[df['country'].isin(country)]
    if business:
        df = df[df['business'] == business]
    if subbusiness:
        df = df[df['subbusiness'] == subbusiness]

    # Group by the specified granularity
    if granularity == "aggregate":
        total_balances = df['balances'].sum()
        return pd.DataFrame({"balances": [total_balances]})
    
    if granularity in ["client", "date", "business", "subbusiness", "region", "country"]:
        # We map granularity to the actual column name
        group_col = 'client_id' if granularity == 'client' else granularity
        
        if group_col not in df.columns:
            return pd.DataFrame({'balances': []})

        # For balances, we typically take the average balance over the period
        agg_df = df.groupby(group_col)['balances'].mean().reset_index()
        return agg_df

    # Fallback for safety
    return pd.DataFrame({'balances': []}) 