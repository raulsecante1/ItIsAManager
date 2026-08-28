# ItIsAManager

Multi-Agent Personal Knowledge Manager (MPKN)

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
graph TD;
  __start__([__start__]) --> investigator_node;
  investigator_node --> outline_node;
  outline_node --> article_node;
  article_node --> rubirc_node;
  rubirc_node -->|write| write_file_node;
  rubirc_node -->|revise| revise_draft_node;
  rubirc_node -->|outline| outline_node;
  revise_draft_node --> rubirc_node;
  write_file_node --> __end__([__end__]);
```

## Tech stack and Environment

- Python 3.13.5
- `LangChain`
- `LangGraph`
- LLM API
- Management via `uv`

## Project structure

```
src/agent_project/
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
    ├── supervisor.py       # Supervisor
    ├── subgraphs/          # 
    │   ├── investigator.py #
    │   ├── synthesizer.py  #
    │   ├── revierer.py     #
    │   ├── generator.py    #
    │   └── writer.py       #
    └── checkpointer.py     # 
```

src/agent_project/
├── schemas.py              # (保留) 数据模型
├── main.py                 # (修改) 调用 Supervisor
├── config/
│   ├── settings.py         # (修改) 增加 MCP、Checkpointer 配置
│   └── logging_config.py   # (保留)
├── tools/
│   ├── agent_tool.py       # (可删除/替换) 由 MCP 工具替代
│   ├── utils.py            # (部分保留) 辅助函数
│   └── reader.py           # (可删除) 由 MCP Server 替代
└── agent/
    ├── supervisor.py       # (新增) 创建 Supervisor
    ├── subgraphs/          # (新增) 存放各个子图
    │   ├── investigator.py 
    │   ├── synthesizer.py
    │   └── writer.py
    └── checkpointer.py     # (新增) 配置 Checkpointer