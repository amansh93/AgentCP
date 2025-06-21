# LangGraph Implementation Documentation

## Overview

This folder contains a parallel implementation of the AgentCP workflow using LangGraph. The implementation mirrors the same architecture as the original but uses LangGraph's graph-based execution model instead of sequential execution.

## Architecture Comparison

### Original Architecture
- **Sequential Execution**: Steps are executed one after another in a linear fashion
- **Single Error Handler**: Centralized error handling in the Executor
- **Manual State Management**: AgentWorkspace manually manages dataframes
- **Fixed Flow**: Planning → Execution → Response Synthesis

### LangGraph Architecture  
- **Graph-Based Execution**: Steps are nodes in a graph with conditional routing
- **Distributed Error Handling**: Each node can handle and recover from errors
- **Built-in State Management**: LangGraph manages state transitions automatically
- **Flexible Flow**: Conditional edges allow dynamic routing based on state

## Key Components

### 1. State Management (`state.py`)
- **AgentState**: TypedDict defining the complete state structure
- **WorkspaceManager**: Utilities for managing dataframes in the state
- **create_initial_state()**: Factory function for creating initial state

### 2. Nodes (`nodes.py`)
- **PlannerNode**: Mirrors MultiStepPlanner functionality
- **ExecutorNode**: Handles individual step execution
- **ErrorHandlerNode**: Manages error recovery and plan correction
- **ResponseSynthesizerNode**: Generates final responses

### 3. Workflow (`workflow.py`)
- **SimplifiedLangGraphWorkflow**: Demo implementation showing the structure
- **Commented LangGraph Code**: Shows how actual LangGraph implementation would look
- **Conditional Logic**: Functions for routing between nodes

### 4. Main Entry Point (`main.py`)
- **main_langgraph()**: Main function mirroring original main_complex()
- **compare_with_original()**: Comparison between implementations

## Installation

1. Install base requirements:
```bash
pip install -r requirements.txt
```

2. Install LangGraph dependencies (optional):
```bash
pip install langgraph langchain-core langchain-openai
```

## Usage

### Basic Usage
```python
from langgraph_agent import main_langgraph

# Run the LangGraph version
main_langgraph()
```

### Workflow Creation
```python
from langgraph_agent import create_workflow

# Create and run workflow
workflow = create_workflow()
result = workflow.run("Your query here")
```

### State Management
```python
from langgraph_agent import create_initial_state, WorkspaceManager

# Create state
state = create_initial_state("Test query")

# Add dataframe
import pandas as pd
df = pd.DataFrame({'col1': [1, 2, 3]})
WorkspaceManager.add_dataframe(state, 'test_df', df)

# Retrieve dataframe
retrieved_df = WorkspaceManager.get_dataframe(state, 'test_df')
```

## Features

### ✅ Implemented
- Complete state management system
- All node implementations (Planner, Executor, Error Handler, Response Synthesizer)
- Workflow routing logic
- Error handling and recovery
- Integration with existing tools
- Comprehensive test suite

### 🚧 With Full LangGraph
When LangGraph is properly installed, the implementation would provide:
- True graph-based execution
- Built-in checkpointing and persistence
- Enhanced debugging and observability
- Parallel execution capabilities
- Advanced error recovery patterns

## Testing

Run the test suite:
```bash
python test_langgraph.py
```

The tests verify:
- State management functionality
- Workflow structure
- Execution logic
- Component integration

## Benefits of LangGraph Implementation

1. **Better Error Handling**: Distributed error handling with recovery at each node
2. **Flexible Routing**: Conditional edges allow dynamic workflow routing
3. **State Persistence**: Built-in state management with checkpointing
4. **Observability**: Better debugging and monitoring capabilities
5. **Scalability**: Support for parallel execution and complex workflows
6. **Modularity**: Each component is a separate node, improving maintainability

## Migration Notes

- **API Compatibility**: Same interfaces as original implementation
- **Tool Reuse**: All existing tools are reused without modification
- **Configuration**: Same configuration and environment variables
- **Output Format**: Same response format and structure

## File Structure

```
langgraph_agent/
├── __init__.py              # Package initialization
├── README.md               # This documentation
├── state.py                # State management
├── nodes.py                # LangGraph nodes
├── workflow.py             # Workflow definition
└── main.py                 # Entry point
```

## Example Output

The LangGraph implementation produces the same output as the original but with enhanced execution flow:

```
============================================================
         LANGGRAPH AGENT VERSION
============================================================

User Query: What were the top 3 systematic clients by revenue growth between last year and this year?

--- LangGraph Workflow initialized ---
--- Starting LangGraph workflow for query: ... ---

--- Workflow Iteration 1 ---
Current status: planning
Next action: plan

--- LangGraph Planner: Creating multi-step plan ---
[... execution continues ...]

==================== FINAL ANSWER ====================
[Final response here]
======================================================

--- Execution Summary ---
Status: completed
Steps executed: 4
Dataframes created: 3
```