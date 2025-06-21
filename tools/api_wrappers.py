import pandas as pd
import numpy as np
from typing import List, Literal, Optional

def get_revenues(
    client_ids: List[str],
    start_date: str,
    end_date: str,
    granularity: Literal["aggregate", "client", "date"],
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC"]] = None,
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None,
) -> pd.DataFrame:
    """
    Placeholder for the get_revenues API.
    Returns a dummy pandas DataFrame based on the specified granularity.
    """
    print(f"--- CALLING get_revenues(client_ids={client_ids}, start_date='{start_date}', end_date='{end_date}', business='{business}', subbusiness='{subbusiness}', granularity='{granularity}') ---")

    if granularity == "aggregate":
        return pd.DataFrame({"Revenues": [np.random.randint(1_000_000, 50_000_000)]})
    
    if granularity == "client":
        num_clients = len(client_ids) if client_ids else 5
        data = {
            "client_id": client_ids if client_ids else [f"cl_id_{i}" for i in range(num_clients)],
            "client_name": [f"Client {i}" for i in range(num_clients)],
            "revenues": np.random.randint(1_000_000, 10_000_000, size=num_clients),
        }
        return pd.DataFrame(data)

    if granularity == "date":
        dates = pd.to_datetime(pd.date_range(start_date, end_date, freq='D'))
        data = {
            "date": dates,
            "revenues": np.random.randint(100_000, 500_000, size=len(dates)),
        }
        return pd.DataFrame(data)

def get_balances(
    client_ids: List[str],
    start_date: str,
    end_date: str,
    granularity: Literal["aggregate", "client", "date"],
    business: Optional[Literal["Prime", "Equities Ex Prime", "FICC"]] = None,
    subbusiness: Optional[Literal["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"]] = None,
) -> pd.DataFrame:
    """
    Placeholder for the get_balances API.
    Returns a dummy pandas DataFrame based on the specified granularity.
    """
    print(f"--- CALLING get_balances(client_ids={client_ids}, start_date='{start_date}', end_date='{end_date}', business='{business}', subbusiness='{subbusiness}', granularity='{granularity}') ---")

    if granularity == "aggregate":
        df = pd.DataFrame({"Balances": [np.random.randint(10_000_000, 500_000_000)]})
    
    elif granularity == "client":
        num_clients = len(client_ids) if client_ids else 5
        data = {
            "client_id": client_ids if client_ids else [f"cl_id_{i}" for i in range(num_clients)],
            "client_name": [f"Client {i}" for i in range(num_clients)],
            "balances": np.random.randint(10_000_000, 100_000_000, size=num_clients),
        }
        df = pd.DataFrame(data)

    elif granularity == "date":
        dates = pd.to_datetime(pd.date_range(start_date, end_date, freq='D'))
        data = {
            "date": dates,
            "balances": np.random.randint(1_000_000, 5_000_000, size=len(dates)),
        }
        df = pd.DataFrame(data)
    
    return df 