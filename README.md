# AgentCP - Intelligent Financial Data Analysis Agent

AgentCP is a sophisticated multi-step intelligent agent system designed for financial data analysis. It leverages Large Language Models (LLMs) to decompose complex natural language queries into structured, executable plans that can fetch, process, and synthesize financial data.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Run web interface
python app.py
```

Visit http://localhost:5001 to interact with the agent through a web interface.

## Key Features

- **Natural Language Processing**: Understands complex financial queries in plain English
- **Multi-Step Planning**: Automatically decomposes complex tasks into manageable steps
- **Self-Correction**: Handles errors intelligently with automatic retry and plan correction
- **Data Integration**: Combines multiple data sources and performs sophisticated analysis
- **Visualization**: Generates plots and charts automatically when requested
- **Web & CLI Interface**: Flexible interaction modes

## Example Queries

- "What were the top 3 clients by revenue growth between 2023 and 2024?"
- "Plot the revenue trend for Millennium since 2023"
- "Compare financing vs execution revenues for Q1 2024"
- "Show me the balance breakdown by region for EMEA clients"

## Architecture

AgentCP uses a multi-component architecture:

1. **MultiStepPlanner** - Decomposes queries using LLM intelligence
2. **Executor** - Executes plans with error handling and self-correction
3. **ResponseSynthesizer** - Generates natural language responses
4. **Tool Ecosystem** - Specialized tools for data fetching, analysis, and visualization
5. **AgentWorkspace** - Short-term memory for intermediate results

## Documentation

For comprehensive documentation about the system architecture and workflow:

- **[Workflow Architecture Documentation](./WORKFLOW_ARCHITECTURE.md)** - Complete system overview, component descriptions, and example workflows
- **[Architecture Diagrams](./ARCHITECTURE_DIAGRAMS.md)** - Detailed visual diagrams and execution flows

## Components

- `agent/` - Core agent components (planner, executor, synthesizer)
- `tools/` - Tool implementations (data fetch, code execution, etc.)
- `knowledge_base/` - Domain-specific knowledge and mappings
- `static/` & `templates/` - Web interface assets
- `app.py` - Flask web application
- `main.py` - Command-line interface

## Requirements

- Python 3.8+
- OpenAI API access
- Dependencies listed in `requirements.txt`

## License

[Add your license information here]