#!/usr/bin/env python3
"""
Demo script for Enhanced Multi-Dimensional Granularity System

This script demonstrates the new multi-dimensional granularity capabilities where
row_granularity can accept up to 2 dimensions for sophisticated data analysis.

Key Features:
- Multi-dimensional row grouping (e.g., ["date", "client"], ["business", "date"])
- Validation to prevent overlaps between row_granularity and col_granularity
- Support for up to 2 dimensions in both row and column granularity
- Comprehensive error handling and validation
"""

from tools.query_tool import SimpleQueryTool, SimpleQueryInput
import pandas as pd

def demonstrate_multi_dimensional_granularity():
    """Demonstrate the new multi-dimensional granularity system."""
    
    print("=" * 80)
    print("ENHANCED MULTI-DIMENSIONAL GRANULARITY DEMONSTRATION")
    print("=" * 80)
    
    tool = SimpleQueryTool()
    
    # 1. Single Dimension (Backward Compatible)
    print("\n1. SINGLE DIMENSION GRANULARITY (Backward Compatible)")
    print("-" * 50)
    query = SimpleQueryInput(
        metric="revenues",
        entities=["millennium", "systematic"],
        date_description="Q1 2024",
        row_granularity=["client"]
    )
    result = tool.execute(query)
    print(f"Single dimension result shape: {result.shape}")
    print(result.head())
    
    # 2. Multi-Dimensional: Date + Client
    print("\n2. MULTI-DIMENSIONAL: Date + Client")
    print("-" * 50)
    query = SimpleQueryInput(
        metric="revenues",
        entities=["millennium", "systematic"],
        date_description="Q1 2024",
        row_granularity=["date", "client"]
    )
    result = tool.execute(query)
    print(f"Date + Client result shape: {result.shape}")
    print("Sample data:")
    print(result.head(10))
    
    # 3. Multi-Dimensional: Business + Date
    print("\n3. MULTI-DIMENSIONAL: Business + Date")
    print("-" * 50)
    query = SimpleQueryInput(
        metric="balances",
        entities=["millennium"],
        date_description="Q1 2024",
        row_granularity=["business", "date"],
        business="Prime"
    )
    result = tool.execute(query)
    print(f"Business + Date result shape: {result.shape}")
    print("Sample data:")
    print(result.head(10))
    
    # 4. Enhanced Granularity: Row + Column Dimensions
    print("\n4. ENHANCED: Multi-Dimensional Rows + Column Pivoting")
    print("-" * 50)
    query = SimpleQueryInput(
        metric="revenues",
        entities=["millennium", "systematic"],
        date_description="Q1 2024",
        row_granularity=["client"],
        col_granularity=["business"]
    )
    result = tool.execute(query)
    print(f"Row + Column granularity result shape: {result.shape}")
    print("Pivoted data:")
    print(result.head())
    
    # 5. Complex Multi-Dimensional Analysis
    print("\n5. COMPLEX: Region + Business Analysis")
    print("-" * 50)
    query = SimpleQueryInput(
        metric="balances",
        entities=["millennium", "systematic", "citadel"],
        date_description="Q1 2024",
        row_granularity=["region", "business"],
        col_granularity=["subbusiness"]
    )
    result = tool.execute(query)
    print(f"Complex analysis result shape: {result.shape}")
    print("Multi-dimensional breakdown:")
    print(result.head())
    
    # 6. Balance Decomposition with Multi-Dimensional Grouping
    print("\n6. BALANCE DECOMPOSITION: Date + Client")
    print("-" * 50)
    query = SimpleQueryInput(
        metric="balances_decomposition",
        entities=["millennium"],
        date_description="Q1 2024",
        row_granularity=["date", "client"]
    )
    result = tool.execute(query)
    print(f"Decomposition result shape: {result.shape}")
    print("Balance decomposition with multi-dimensional grouping:")
    print(result.head())
    
    # 7. Capital Metrics with Multi-Dimensional Analysis
    print("\n7. CAPITAL METRICS: Business + Subbusiness")
    print("-" * 50)
    query = SimpleQueryInput(
        metric="Total AE",
        entities=["millennium"],
        date_description="Q1 2024",
        row_granularity=["business", "subbusiness"],
        col_granularity=["region"]
    )
    result = tool.execute(query)
    print(f"Capital metrics result shape: {result.shape}")
    print("Capital analysis by business and region:")
    print(result.head())

def demonstrate_validation_features():
    """Demonstrate the validation features of the enhanced granularity system."""
    
    print("\n" + "=" * 80)
    print("GRANULARITY VALIDATION DEMONSTRATIONS")
    print("=" * 80)
    
    # Test 1: Duplicate values in row_granularity
    print("\n1. Testing Duplicate Values in row_granularity")
    print("-" * 50)
    try:
        query = SimpleQueryInput(
            metric="revenues",
            entities=["millennium"],
            date_description="Q1 2024",
            row_granularity=["client", "client"]  # Duplicate
        )
        print("ERROR: Should have failed!")
    except ValueError as e:
        print(f"✓ Correctly rejected duplicate values: {e}")
    
    # Test 2: Aggregate with other values
    print("\n2. Testing Aggregate with Other Values")
    print("-" * 50)
    try:
        query = SimpleQueryInput(
            metric="revenues",
            entities=["millennium"],
            date_description="Q1 2024",
            row_granularity=["aggregate", "client"]  # Invalid combination
        )
        print("ERROR: Should have failed!")
    except ValueError as e:
        print(f"✓ Correctly rejected aggregate combination: {e}")
    
    # Test 3: Overlap between row and column granularity
    print("\n3. Testing Row/Column Granularity Overlap")
    print("-" * 50)
    try:
        query = SimpleQueryInput(
            metric="revenues",
            entities=["millennium"],
            date_description="Q1 2024",
            row_granularity=["client", "business"],
            col_granularity=["business", "region"]  # 'business' overlaps
        )
        print("ERROR: Should have failed!")
    except ValueError as e:
        print(f"✓ Correctly rejected overlapping granularities: {e}")
    
    # Test 4: Too many dimensions
    print("\n4. Testing Maximum Dimension Limit")
    print("-" * 50)
    try:
        query = SimpleQueryInput(
            metric="revenues",
            entities=["millennium"],
            date_description="Q1 2024",
            row_granularity=["client", "business", "date"]  # Too many dimensions
        )
        print("ERROR: Should have failed!")
    except ValueError as e:
        print(f"✓ Correctly rejected too many dimensions: {e}")
    
    # Test 5: Valid complex combination
    print("\n5. Testing Valid Complex Combination")
    print("-" * 50)
    try:
        query = SimpleQueryInput(
            metric="revenues",
            entities=["millennium"],
            date_description="Q1 2024",
            row_granularity=["date", "client"],
            col_granularity=["business", "region"]  # No overlap, valid
        )
        print("✓ Successfully created valid complex granularity combination")
    except ValueError as e:
        print(f"ERROR: Should have succeeded: {e}")

def demonstrate_use_cases():
    """Demonstrate real-world use cases for multi-dimensional granularity."""
    
    print("\n" + "=" * 80)
    print("REAL-WORLD USE CASE DEMONSTRATIONS")
    print("=" * 80)
    
    tool = SimpleQueryTool()
    
    # Use Case 1: Time Series Analysis Per Client
    print("\n1. USE CASE: Time Series Analysis Per Client")
    print("-" * 50)
    print("Business Question: How do revenues trend over time for each client?")
    query = SimpleQueryInput(
        metric="revenues",
        entities=["millennium", "systematic", "citadel"],
        date_description="Q1 2024",
        row_granularity=["date", "client"]
    )
    result = tool.execute(query)
    print(f"Result: {result.shape[0]} data points across {len(result['client_id'].unique()) if 'client_id' in result.columns else 0} clients")
    print("Perfect for time series plotting with multiple client lines")
    
    # Use Case 2: Business Performance Analysis
    print("\n2. USE CASE: Business Line Performance Over Time")
    print("-" * 50)
    print("Business Question: How does each business line perform month-to-month?")
    query = SimpleQueryInput(
        metric="revenues",
        entities=["millennium"],
        date_description="Q1 2024",
        row_granularity=["business", "date"],
        col_granularity=["fin_or_exec"]
    )
    result = tool.execute(query)
    print(f"Result: Business performance data with financing/execution breakdown")
    print("Ideal for business line trend analysis and comparison")
    
    # Use Case 3: Regional Analysis
    print("\n3. USE CASE: Regional Business Analysis")
    print("-" * 50)
    print("Business Question: How do different regions contribute to each business line?")
    query = SimpleQueryInput(
        metric="balances",
        entities=["millennium", "systematic"],
        date_description="Q1 2024",
        row_granularity=["region", "business"],
        col_granularity=["subbusiness"]
    )
    result = tool.execute(query)
    print(f"Result: Regional breakdown with subbusiness detail")
    print("Great for geographic performance analysis")
    
    # Use Case 4: Client Balance Evolution
    print("\n4. USE CASE: Client Balance Evolution with Decomposition")
    print("-" * 50)
    print("Business Question: How do client balances change over time with component breakdown?")
    query = SimpleQueryInput(
        metric="balances_decomposition",
        entities=["millennium"],
        date_description="Q1 2024",
        row_granularity=["date", "client"]
    )
    result = tool.execute(query)
    print(f"Result: Daily balance evolution per client with component breakdown")
    print("Essential for tracking balance changes and understanding drivers")

if __name__ == "__main__":
    print("Starting Enhanced Multi-Dimensional Granularity Demo...")
    
    # Main feature demonstrations
    demonstrate_multi_dimensional_granularity()
    
    # Validation demonstrations
    demonstrate_validation_features()
    
    # Real-world use cases
    demonstrate_use_cases()
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("✓ row_granularity now supports up to 2 dimensions for sophisticated analysis")
    print("✓ Multi-dimensional grouping enables complex business insights")
    print("✓ Robust validation prevents invalid granularity combinations")
    print("✓ Backward compatibility maintained for existing single-dimension usage")
    print("✓ Perfect for time series, regional, and business line analysis")
    print("\nThe enhanced granularity system provides powerful new capabilities")
    print("for multi-dimensional data analysis while maintaining system reliability!") 