from tools.resolvers import resolve_clients, resolve_dates
from datetime import datetime

def run_resolver_tests():
    """
    Runs a series of tests on the resolver functions to ensure they work as expected.
    """
    print("--- Running Resolver Tests ---")

    # Test cases for client resolver
    print("\n--- Testing resolve_clients ---")
    test_cases_clients = {
        "Simple lookup": (["millennium"], ["cl_id_millennium"]),
        "Typo handling": (["pont 72"], ["cl_id_point72"]),
        "Group expansion": (["systematic"], ["cl_id_twosigma", "cl_id_citadel", "cl_id_some_other_quant"]),
        "Mixed list": (["Citadel", "quant"], ["cl_id_citadel", "cl_id_twosigma", "cl_id_some_other_quant"]),
        "Deduplication": (["Citadel", "systematic"], ["cl_id_citadel", "cl_id_twosigma", "cl_id_some_other_quant"]),
        "Unknown entity": (["not_a_real_client"], []),
    }

    for name, (inputs, expected) in test_cases_clients.items():
        # Sort lists to ensure comparison is order-independent
        result = sorted(resolve_clients(inputs))
        expected = sorted(expected)
        assert result == expected, f"'{name}' FAILED: Expected {expected}, got {result}"
        print(f"'{name}' PASSED")

    # Test cases for date resolver
    print("\n--- Testing resolve_dates ---")
    
    current_year = datetime.now().year
    last_year = current_year - 1
    
    test_cases_dates = {
        "Simple Quarter": ("q1 2024", ("2024-01-01", "2024-03-31")),
        "Quarter with 'qtr'": ("qtr 2 2024", ("2024-04-01", "2024-06-30")),
        "Fiscal Year": ("fy'25", ("2024-10-01", "2025-09-30")),
        "Simple Year": ("2023", ("2023-01-01", "2023-12-31")),
        "Relative Year": ("last year", (f"{last_year}-01-01", f"{last_year}-12-31")),
    }
    
    for name, (inputs, expected) in test_cases_dates.items():
        result = resolve_dates(inputs)
        assert result == expected, f"'{name}' FAILED: Expected {expected}, got {result}"
        print(f"'{name}' PASSED")

    print("\n--- All Resolver Tests Passed ---")

if __name__ == "__main__":
    run_resolver_tests() 