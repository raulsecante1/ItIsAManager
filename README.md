# ItIsAManager

Multi-Agent Personal Knowledge Manager (MPKN)

- custom state graph, deterministic workflow version at manual_state_graph branch
- ReAct and MCP version at react_mcp branch

## What it is?

MPKN is a Multi-agent project based on  *LangChain*, that able to read the documents, notes, summarize the key points, and then generate new contests based on the summaries.

## Quick Start

1. Clone the project

1. Install `uv` or create a virtual environment via`-venv`

1. run the project via `uv run itisamaster` or `python main.py` the other case

## Workflow

The `main_agent` receives the reuqest from the user like:

```
You are an expert article generation agent.
Now i need you to read the files at "documents/" then generate an article based on it
```

Then create a `sub_agent` as an investigator, which has the tool to `list` and `read` the files from the path give by the user, between them the `read` tool will start some `llm_models` to read the `exact_content` of the file, and generate the `knowledge_chunk` based on the `exact_content` read by the `llm_models`.

After that some other `llm_models` will be started to generate `outline`, `chapter`s based on the `knowledge_chunk`.

When `outline` is synthesized, serval other `llm_models` will be started to generate `final_draft`, then the `main_agent` will use its tool `write` to wirte down the article

```mermaid
graph TD
    A[User Request] --> B(Master Agent)
    B --> C{Need to read files?}
    C -->|Yes| D[Call SubAgent: Investigator]
    D --> E[Call read_note tool]
    E --> F[Return KnowledgeChunk list]
    F --> B
    C -->|No| H[Generate ArticleOutline]
    H --> I[Generate FinalDraft by chapters]
    I --> J[RubricMiddleware: Self-score]
    J -->|Score < 8| K[Revise draft with feedback]
    K --> I
    J -->|Score >= 8| L[Call write_article tool]
    L --> M[Write to disk]
```

## Tech stack and Environment

- Python 3.13.5
- `LangChain`
- `LangGraph`
- `DeepAgents`
- LLM API
- Management via `uv`

## Project structure

```
src/itisamanager/
├── schemas.py              # Pydantic dataformat
├── main.py                 # 
├── config/                 #
│   ├── settings.py         # Configuration of the project
│   └── logging_config.py   # Configuration of the log putput
├── tools/                  # Tools
│   ├── agent_tool.py       # Agentes' tool for varios operations
│   ├── utils.py            # Varios utilities
│   └── reader.py           # Varios file readers for distinct file formats
└── agent/                  # Agent
│   └── agent.py            # 
```
