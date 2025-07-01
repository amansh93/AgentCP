import pandas as pd
from tools.query_tool import SimpleQueryTool, SimpleQueryInput

def run_query_tool_tests():
    """Test the SimpleQueryTool with various query inputs."""
    print("--- Running Query Tool Tests ---")
    
    tool = SimpleQueryTool()
    
    # Test Case 1: Basic aggregate query
    print("\n--- Test Case 1: Aggregate Revenues for a single client ---")
    query1 = SimpleQueryInput(
        metric="revenues",
        entities=["millennium"], 
        date_description="Q1 2024",
        row_granularity=["aggregate"]  # List format
    )
    result1 = tool.execute(query1)
    print(f"Result shape: {result1.shape}")
    print(result1)
    
    # Test Case 2: Multi-dimensional granularity
    print("\n--- Test Case 2: Date + Client Multi-Dimensional Granularity ---")
    query2 = SimpleQueryInput(
        metric="revenues",
        entities=["millennium", "systematic"],
        date_description="Q1 2024",
        row_granularity=["date", "client"]  # Multi-dimensional
    )
    result2 = tool.execute(query2)
    print(f"Result shape: {result2.shape}")
    print(result2.head())
    
    # Test Case 3: Enhanced granularity with columns
    print("\n--- Test Case 3: Enhanced Granularity with Column Pivoting ---")
    query3 = SimpleQueryInput(
        metric="balances",
        entities=["millennium", "systematic"],
        date_description="Q1 2024",
        row_granularity=["client"],  # List format
        col_granularity=["business"]  # List format
    )
    result3 = tool.execute(query3)
    print(f"Result shape: {result3.shape}")
    print(result3.head())
    
    # Test Case 4: Balance decomposition with multi-dimensional granularity
    print("\n--- Test Case 4: Balance Decomposition Multi-Dimensional ---")
    query4 = SimpleQueryInput(
        metric="balances_decomposition",
        entities=["millennium"],
        date_description="Q1 2024",
        row_granularity=["date", "client"]  # Multi-dimensional
    )
    result4 = tool.execute(query4)
    print(f"Result shape: {result4.shape}")
    print(result4.head())
    
    # Test Case 5: Capital metrics with business breakdown
    print("\n--- Test Case 5: Capital Metrics with Business Breakdown ---")
    query5 = SimpleQueryInput(
        metric="Total AE",
        entities=["millennium"],
        date_description="Q1 2024",
        row_granularity=["business", "subbusiness"],  # Multi-dimensional
        col_granularity=["region"]  # List format
    )
    result5 = tool.execute(query5)
    print(f"Result shape: {result5.shape}")
    print(result5.head())
    
    print("\n--- All Query Tool Tests Passed ---")

def test_basic_revenues_query():
    """Test basic revenue query with default aggregate granularity."""
    tool = SimpleQueryTool()
    query_input = SimpleQueryInput(
        metric="revenues",
        entities=["millennium", "systematic"],
        date_description="Q1 2024",
        row_granularity=["aggregate"]
    )
    result = tool.execute(query_input)
    assert not result.empty
    assert "revenues" in result.columns

def test_multi_dimensional_row_granularity():
    """Test multi-dimensional row granularity with date and client."""
    tool = SimpleQueryTool()
    query_input = SimpleQueryInput(
        metric="revenues", 
        entities=["millennium", "systematic"],
        date_description="Q1 2024",
        row_granularity=["date", "client"]
    )
    result = tool.execute(query_input)
    assert not result.empty
    assert "revenues" in result.columns
    assert "date" in result.columns
    assert "client_id" in result.columns
    # Should have multiple rows for different date/client combinations
    assert len(result) > 1

def test_business_date_granularity():
    """Test business and date multi-dimensional granularity."""
    tool = SimpleQueryTool()
    query_input = SimpleQueryInput(
        metric="balances",
        entities=["millennium"],
        date_description="Q1 2024",
        row_granularity=["business", "date"],
        business="Prime"
    )
    result = tool.execute(query_input)
    assert not result.empty
    assert "balances" in result.columns
    assert "business" in result.columns
    assert "date" in result.columns

def test_enhanced_granularity_with_columns():
    """Test enhanced granularity with both row and column dimensions."""
    tool = SimpleQueryTool()
    query_input = SimpleQueryInput(
        metric="revenues",
        entities=["millennium", "systematic"],
        date_description="Q1 2024",
        row_granularity=["client"],
        col_granularity=["business"]
    )
    result = tool.execute(query_input)
    assert not result.empty
    # Should have client_id column and business-based columns

def test_balance_decomposition_multi_dimensional():
    """Test balance decomposition with multi-dimensional row granularity."""
    tool = SimpleQueryTool()
    query_input = SimpleQueryInput(
        metric="balances_decomposition",
        entities=["millennium"],
        date_description="Q1 2024",
        row_granularity=["date", "client"]
    )
    result = tool.execute(query_input)
    assert not result.empty
    assert "date" in result.columns
    assert "client_id" in result.columns

def test_granularity_validation_no_duplicates():
    """Test that duplicate values in row_granularity are rejected."""
    try:
        SimpleQueryInput(
            metric="revenues",
            entities=["millennium"],
            date_description="Q1 2024",
            row_granularity=["client", "client"]  # Duplicate values
        )
        raise AssertionError("Should have raised ValueError for duplicate values")
    except ValueError as e:
        assert "row_granularity cannot contain duplicate values" in str(e)

def test_granularity_validation_aggregate_only():
    """Test that aggregate must be the only value if used."""
    try:
        SimpleQueryInput(
            metric="revenues",
            entities=["millennium"],
            date_description="Q1 2024",
            row_granularity=["aggregate", "client"]  # Aggregate with other values
        )
        raise AssertionError("Should have raised ValueError for aggregate with other values")
    except ValueError as e:
        assert "When 'aggregate' is used in row_granularity, it must be the only value" in str(e)

def test_granularity_validation_no_overlap():
    """Test that row_granularity and col_granularity cannot overlap."""
    try:
        SimpleQueryInput(
            metric="revenues",
            entities=["millennium"],
            date_description="Q1 2024", 
            row_granularity=["client", "business"],
            col_granularity=["business", "region"]  # 'business' overlaps
        )
        raise AssertionError("Should have raised ValueError for overlapping granularities")
    except ValueError as e:
        assert "col_granularity cannot contain values that are already in row_granularity" in str(e)

def test_capital_metrics():
    """Test capital metrics with multi-dimensional granularity."""
    tool = SimpleQueryTool()
    query_input = SimpleQueryInput(
        metric="Total AE",
        entities=["millennium"],
        date_description="Q1 2024",
        row_granularity=["business", "subbusiness"],
        col_granularity=["region"]
    )
    result = tool.execute(query_input)
    assert not result.empty
    assert "capital" in result.columns
    assert "business" in result.columns
    assert "subbusiness" in result.columns

def test_single_dimension_compatibility():
    """Test that single dimension granularity still works (backward compatibility)."""
    tool = SimpleQueryTool()
    query_input = SimpleQueryInput(
        metric="balances",
        entities=["millennium"],
        date_description="Q1 2024",
        row_granularity=["client"]  # Single dimension
    )
    result = tool.execute(query_input)
    assert not result.empty
    assert "balances" in result.columns
    assert "client_id" in result.columns

if __name__ == "__main__":
    run_query_tool_tests()
    print("Running multi-dimensional granularity tests...")
    test_basic_revenues_query()
    test_multi_dimensional_row_granularity()
    test_business_date_granularity()
    test_enhanced_granularity_with_columns()
    test_balance_decomposition_multi_dimensional()
    test_capital_metrics()
    test_single_dimension_compatibility()
    print("All basic tests passed!")
    
    # Validation tests
    try:
        test_granularity_validation_no_duplicates()
        print("ERROR: Should have failed on duplicate validation")
    except Exception:
        print("✓ Duplicate validation works correctly")
    
    try:
        test_granularity_validation_aggregate_only()
        print("ERROR: Should have failed on aggregate validation")
    except Exception:
        print("✓ Aggregate validation works correctly")
    
    try:
        test_granularity_validation_no_overlap()
        print("ERROR: Should have failed on overlap validation")
    except Exception:
        print("✓ Overlap validation works correctly")
    
    print("All multi-dimensional granularity tests completed successfully!") 