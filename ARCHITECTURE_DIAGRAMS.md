# AgentCP Architecture Diagrams

This file contains detailed architectural diagrams and visualizations for the AgentCP system.

## System Architecture Layers

```
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                                USER INTERFACE LAYER                              ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║  ┌─────────────────────────┐         ┌─────────────────────────────────────────┐ ║
║  │     Flask Web App       │         │          CLI Interface              │ ║
║  │  ┌─────────────────┐   │         │   ┌─────────────────────────────────┐ │ ║
║  │  │  index.html     │   │         │   │      main.py                    │ │ ║
║  │  │  static/        │   │         │   │   (Direct execution)            │ │ ║
║  │  │  - script.js    │   │         │   └─────────────────────────────────┘ │ ║
║  │  │  - style.css    │   │         └─────────────────────────────────────────┘ ║
║  │  └─────────────────┘   │                                                   ║
║  └─────────────────────────┘                                                   ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                 AGENT CORE LAYER                                 ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║  ┌─────────────────────────────────────────────────────────────────────────────┐ ║
║  │                         MAIN ORCHESTRATION                                  │ ║
║  │                                                                             │ ║
║  │  ┌─────────────────┐   ┌──────────────────┐   ┌───────────────────────────┐ │ ║
║  │  │ MultiStepPlanner│──▶│     Executor     │──▶│   ResponseSynthesizer     │ │ ║
║  │  │                 │   │                  │   │                           │ │ ║
║  │  │ • Query Analysis│   │ • Plan Execution │   │ • Natural Language        │ │ ║
║  │  │ • LLM Integration│   │ • Tool Orchestr. │   │   Generation              │ │ ║
║  │  │ • Plan Creation │   │ • Error Handling │   │ • Response Formatting     │ │ ║
║  │  │ • Strategic     │   │ • Self-Correction│   │ • Domain Adaptation       │ │ ║
║  │  │   Decomposition │   │ • Retry Logic    │   │                           │ │ ║
║  │  └─────────────────┘   └──────────────────┘   └───────────────────────────┘ │ ║
║  └─────────────────────────────────────────────────────────────────────────────┘ ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                              SUPPORT SERVICES LAYER                              ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║  ┌─────────────────────────┐         ┌─────────────────────────────────────────┐ ║
║  │   AgentWorkspace        │         │           LLM Client                    │ ║
║  │                         │         │                                         │ ║
║  │ ┌─────────────────────┐ │         │  ┌─────────────────────────────────────┐ │ ║
║  │ │   DataFrame Store   │ │         │  │        OpenAI API Client            │ │ ║
║  │ │                     │ │         │  │                                     │ │ ║
║  │ │ Key-value pairs:    │ │         │  │  • GPT-4 (Planning)                │ │ ║
║  │ │ "rev_2023": df1     │ │         │  │  • GPT-4 (Synthesis)               │ │ ║
║  │ │ "rev_2024": df2     │ │         │  │  • GPT-3.5-turbo (Date Parsing)    │ │ ║
║  │ │ "growth_data": df3  │ │         │  └─────────────────────────────────────┘ │ ║
║  │ └─────────────────────┘ │         └─────────────────────────────────────────┘ ║
║  └─────────────────────────┘                                                   ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                  TOOLS LAYER                                     ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║  ┌────────────────┐ ┌────────────────┐ ┌──────────────┐ ┌──────────────────────┐ ║
║  │   data_fetch   │ │ code_executor  │ │describe_df   │ │    Other Tools       │ ║
║  │                │ │                │ │              │ │                      │ ║
║  │ • API Calls    │ │ • Python Exec  │ │• Schema Info │ │ • inform_user        │ ║
║  │ • Data Resolve │ │ • Pandas/NumPy │ │• Column List │ │ • get_valid_business │ ║
║  │ • Validation   │ │ • Matplotlib   │ │• Data Types  │ │   _lines             │ ║
║  │ • DataFrame    │ │ • Plot Saving  │ │              │ │                      │ ║
║  │   Creation     │ │ • Workspace    │ │              │ │                      │ ║
║  │                │ │   Integration  │ │              │ │                      │ ║
║  └────────────────┘ └────────────────┘ └──────────────┘ └──────────────────────┘ ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                            KNOWLEDGE & DATA LAYER                                ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║  ┌─────────────────────────┐         ┌─────────────────────────────────────────┐ ║
║  │    Knowledge Base       │         │         External APIs                  │ ║
║  │                         │         │                                         │ ║
║  │ ┌─────────────────────┐ │         │  ┌─────────────────────────────────────┐ │ ║
║  │ │   Client Data       │ │         │  │       Financial Data APIs          │ │ ║
║  │ │                     │ │         │  │                                     │ ║
║  │ │ • Client Mappings   │ │         │  │  • Revenue API                      │ ║
║  │ │ • Group Definitions │ │         │  │  • Balance API                      │ ║
║  │ │ • Business Lines    │ │         │  │  • Date-based Queries               │ ║
║  │ │ • Region Mappings   │ │         │  │  • Multi-dimensional Filtering      │ ║
║  │ │ • Alias Resolution  │ │         │  │                                     │ ║
║  │ └─────────────────────┘ │         │  └─────────────────────────────────────┘ │ ║
║  └─────────────────────────┘         └─────────────────────────────────────────┘ ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
```

## Component Interaction Diagram

```
     USER QUERY                 RESPONSE
         │                         ▲
         ▼                         │
    ┌─────────────────────────────────────────┐
    │          FLASK WEB APP                  │
    │                                         │
    │  Route: /ask                            │
    │  Method: POST                           │
    │  Content-Type: application/json         │
    └─────────────────────────────────────────┘
         │                         ▲
         ▼                         │
    ╔═════════════════════════════════════════╗
    ║            AGENT CORE                   ║
    ╠═════════════════════════════════════════╣
    ║  ┌─────────────────┐                   ║
    ║  │ MultiStepPlanner│                   ║
    ║  │                 │                   ║
    ║  │ Input: Query    │──┐                ║
    ║  │ Output: Plan    │  │                ║
    ║  └─────────────────┘  │                ║
    ║           │            │                ║
    ║           ▼            │                ║
    ║  ┌─────────────────┐   │                ║
    ║  │    Executor     │   │                ║
    ║  │                 │   │                ║
    ║  │ Input: Plan     │   │ Self-Correction║
    ║  │ Output: Results │   │ Loop           ║
    ║  └─────────────────┘   │                ║
    ║           │            │                ║
    ║           ▼            │                ║
    ║  ┌─────────────────┐   │                ║
    ║  │ResponseSynth.   │◄──┘                ║
    ║  │                 │                    ║
    ║  │ Input: Results  │                    ║
    ║  │ Output: Response│                    ║
    ║  └─────────────────┘                    ║
    ╚═════════════════════════════════════════╝
         │                         ▲
         ▼                         │
    ┌─────────────────────────────────────────┐
    │             TOOLS                       │
    │                                         │
    │  ┌──────────┐ ┌──────────┐ ┌─────────┐ │
    │  │data_fetch│ │code_exec │ │other    │ │
    │  └──────────┘ └──────────┘ └─────────┘ │
    └─────────────────────────────────────────┘
```

## Detailed Execution Flow

```
Phase 1: Query Analysis & Planning
═══════════════════════════════════
    User Query
         │
         ▼
    ┌─────────────────────────────────────────┐
    │         MultiStepPlanner                │
    │                                         │
    │  1. Parse natural language query        │
    │  2. Identify required data sources      │
    │  3. Determine tool sequence             │
    │  4. Validate parameters                 │
    │  5. Create structured plan              │
    └─────────────────────────────────────────┘
         │
         ▼
    MultiStepPlan Object
    ┌─────────────────────────────────────────┐
    │  plan: [                                │
    │    {                                    │
    │      tool_name: "data_fetch",           │
    │      summary: "...",                    │
    │      parameters: {...}                  │
    │    },                                   │
    │    {                                    │
    │      tool_name: "code_executor",        │
    │      summary: "...",                    │
    │      parameters: {...}                  │
    │    }                                    │
    │  ]                                      │
    └─────────────────────────────────────────┘

Phase 2: Plan Execution
══════════════════════
    MultiStepPlan
         │
         ▼
    ┌─────────────────────────────────────────┐
    │            Executor                     │
    │                                         │
    │  For each step in plan:                 │
    │    ┌─────────────────────────────────┐  │
    │    │  1. Extract tool & parameters   │  │
    │    │  2. Execute tool                │  │
    │    │  3. Handle errors/retries       │  │
    │    │  4. Update workspace            │  │
    │    │  5. Track progress              │  │
    │    └─────────────────────────────────┘  │
    │                                         │
    │  Error Handling:                        │
    │    ┌─────────────────────────────────┐  │
    │    │  If step fails:                 │  │
    │    │    - Retry up to 2 times        │  │
    │    │    - If max retries exceeded:   │  │
    │    │      • Request plan correction  │  │
    │    │      • Replace remaining steps  │  │
    │    │      • Continue execution       │  │
    │    └─────────────────────────────────┘  │
    └─────────────────────────────────────────┘
         │
         ▼
    Final Workspace + Execution Summaries

Phase 3: Response Generation
═══════════════════════════════
    Workspace Data
         │
         ▼
    ┌─────────────────────────────────────────┐
    │        ResponseSynthesizer              │
    │                                         │
    │  1. Analyze original query context      │
    │  2. Extract relevant data from workspace│
    │  3. Format data appropriately           │
    │  4. Generate natural language response  │
    │  5. Include tables/charts as needed     │
    └─────────────────────────────────────────┘
         │
         ▼
    Natural Language Response
    ┌─────────────────────────────────────────┐
    │  "Based on the analysis, the top 3      │
    │   clients by revenue growth are:        │
    │                                         │
    │   | Client    | 2023 Rev | 2024 Rev |  │
    │   |-----------|----------|----------|  │
    │   | ClientA   | $50M     | $75M     |  │
    │   | ClientB   | $30M     | $45M     |  │
    │   | ClientC   | $40M     | $55M     |  │
    │                                         │
    │   The highest growth was achieved by... │
    └─────────────────────────────────────────┘
```

## Tool Execution Patterns

### Data Fetch Tool Flow
```
data_fetch Parameters
    │
    ├─ metric: "revenues"|"balances"
    ├─ entities: [client names/groups]  
    ├─ date_description: natural language
    ├─ granularity: aggregation level
    ├─ filters: region/business/etc.
    └─ output_variable: workspace key
         │
         ▼
┌─────────────────────────────────────────┐
│         Entity Resolution               │
│                                         │
│  resolve_clients(entities)              │
│  resolve_dates(date_description)        │
│  resolve_regions(regions)               │
│  resolve_fin_or_exec(fin_or_exec)       │
│  resolve_primary_or_secondary(...)      │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│           API Call                      │
│                                         │
│  if metric == "revenues":               │
│    get_revenues(resolved_params)        │
│  elif metric == "balances":             │
│    get_balances(resolved_params)        │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│        DataFrame Creation               │
│                                         │
│  Convert API response to pandas DF     │
│  Apply data type corrections           │
│  Add metadata columns                  │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│       Workspace Storage                 │
│                                         │
│  workspace.add_df(output_variable, df)  │
└─────────────────────────────────────────┘
```

### Code Executor Tool Flow
```
code_executor Parameters
    │
    └─ code: Python code string
         │
         ▼
┌─────────────────────────────────────────┐
│        Execution Environment           │
│                                         │
│  local_scope = {                        │
│    'dataframes': workspace.dataframes,  │
│    'pd': pandas,                        │
│    'plt': matplotlib.pyplot,            │
│    'np': numpy                          │
│  }                                      │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│          Code Execution                 │
│                                         │
│  exec(code, globals, local_scope)       │
│                                         │
│  Available operations:                  │
│  • DataFrame manipulations              │
│  • Statistical analysis                 │
│  • Plot generation                      │
│  • File I/O (controlled)                │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│        Result Processing                │
│                                         │
│  workspace.dataframes =                 │
│    local_scope['dataframes']            │
│                                         │
│  Handle plot file paths                 │
│  Validate output DataFrames             │
└─────────────────────────────────────────┘
```

## Error Handling Flow

```
                    Step Execution
                          │
                          ▼
                    ┌─────────────┐
                    │   Success?  │
                    └─────────────┘
                          │
                 ┌────────┴────────┐
                 │                 │
               Yes                No
                 │                 │
                 ▼                 ▼
        ┌─────────────────┐ ┌─────────────────┐
        │  Continue to    │ │  Increment      │
        │   Next Step     │ │  Retry Counter  │
        └─────────────────┘ └─────────────────┘
                                   │
                                   ▼
                            ┌─────────────────┐
                            │ Retries < 2?    │
                            └─────────────────┘
                                   │
                          ┌────────┴────────┐
                          │                 │
                        Yes                No
                          │                 │
                          ▼                 ▼
                 ┌─────────────────┐ ┌─────────────────┐
                 │   Retry Same    │ │  Generate       │
                 │     Step        │ │  Correction     │
                 └─────────────────┘ │   Prompt        │
                          │          └─────────────────┘
                          │                 │
                          └─────────┐       ▼
                                   │ ┌─────────────────┐
                                   │ │  Request New    │
                                   │ │  Plan from      │
                                   │ │   Planner       │
                                   │ └─────────────────┘
                                   │        │
                                   │        ▼
                                   │ ┌─────────────────┐
                                   │ │  Replace        │
                                   │ │  Remaining      │
                                   │ │   Steps         │
                                   │ └─────────────────┘
                                   │        │
                                   │        ▼
                                   │ ┌─────────────────┐
                                   └▶│  Continue       │
                                     │  Execution      │
                                     └─────────────────┘
```

This comprehensive visual documentation provides multiple perspectives on the AgentCP architecture, from high-level system design to detailed execution flows and error handling patterns.