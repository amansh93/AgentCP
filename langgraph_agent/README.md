# LangGraph Agent Implementation

This folder contains a parallel implementation of the AgentCP workflow using LangGraph.
The implementation mirrors the same architecture as the original but uses LangGraph's 
graph-based execution model instead of sequential execution.

## Structure

- `state.py` - State management (mirrors AgentWorkspace)
- `nodes.py` - LangGraph nodes for each component
- `workflow.py` - LangGraph workflow definition  
- `main.py` - Entry point for LangGraph version
- `tools/` - Tool implementations (reused from parent)

## Usage

```python
from langgraph_agent.main import main_langgraph

# Run the LangGraph version
main_langgraph()
```