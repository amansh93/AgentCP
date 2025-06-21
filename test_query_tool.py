from tools.query_tool import SimpleQueryTool, SimpleQueryInput

def run_query_tool_tests():
    """
    Tests the SimpleQueryTool to ensure it correctly orchestrates
    resolvers and API wrappers.
    """
    print("--- Running Query Tool Tests ---")
    tool = SimpleQueryTool()

    # Test Case 1: A simple aggregate query
    print("\n--- Test Case 1: Aggregate Revenues for a single client ---")
    query1 = SimpleQueryInput(
        metric="revenues",
        entities=["millennium"],
        date_description="q1 2024",
        business="Prime",
        subbusiness="PB",
        granularity="aggregate"
    )
    result1 = tool.execute(query1)
    assert not result1.empty
    assert "Revenues" in result1.columns
    print("Resulting DataFrame:")
    print(result1)
    print("Test Case 1 PASSED")

    # Test Case 2: A client-level query for a group
    print("\n--- Test Case 2: Client-level Balances for a group ---")
    query2 = SimpleQueryInput(
        metric="balances",
        entities=["systematic"],
        date_description="last year",
        business="FICC",
        subbusiness="Macro",
        granularity="client"
    )
    result2 = tool.execute(query2)
    assert not result2.empty
    assert "balances" in result2.columns
    assert len(result2) > 1 # Should get multiple clients for the group
    print("Resulting DataFrame:")
    print(result2)
    print("Test Case 2 PASSED")

    print("\n--- All Query Tool Tests Passed ---")

if __name__ == "__main__":
    run_query_tool_tests() 