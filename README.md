# ItIsAManager

Multi-Agent Personal Knowledge Manager (MPKM)

- custom state graph, deterministic workflow version at manual_state_graph branch
- ReAct and MCP version at react_mcp branch

## What it is?

MPKN is a Multi-agent project based on  *LangChain*, that able to read the documents, notes, summarize the key points, and then generate new contests based on the summaries.

## Quick Start

1. Clone the project

1. Install `uv` or create a virtual environment via`-venv`

1. run the project via `uv run itisamanager` or `python main.py` the other case

## Workflow

The `supervisor` graph receives the reuqest from the user like:

```
You are an expert article generation agent.
Now i need you to read the files at "documents/" then generate an article based on it
```

Along with a path `{working_directory}/documents`

Then calls the `investigator` sub graph, which has access to a mcp server where holds `read_file` and `list_readable_file` tools, and a local tool `read_note`, then the invesigator will start the loop of read files, think if need to read more, read file,... until it decides that there are enough files readed, it will call the `read_note` tool, where some `llm_models` will be started  to read the `file_content` of the readed file, and generate the `knowledge_chunk` based on the `exact_content` read by the `llm_models`.

After that is the `synthesizer` sub graph, where some other `llm_models` will be started to generate `outline`, `chapter`s based on the `knowledge_chunk`.

When `outline` is synthesized, it comes to `generator` graph, where serval other `llm_models` will be started to generate `final_draft`, then the `reviewer` sub graph will start to judge whether the generated articl is good enough (score>8) to write into a file (if not the flow will back to the former sub graph).

So when all there are finished, the `writer` subgraph will be initiated to write the file.

```mermaid
flowchart TB
    __start__(["__start__"]) --> investigator_node["investigator_node"]
    investigator_node --> outline_node["outline_node"] & investigator_node
    outline_node --> article_node["article_node"]
    article_node --> rubirc_node["rubirc_node"]
    rubirc_node -- write --> write_file_node["write_file_node"]
    rubirc_node -- revise --> revise_draft_node["revise_draft_node"]
    rubirc_node -- outline --> outline_node
    revise_draft_node --> rubirc_node
    write_file_node --> __end__(["__end__"])


    L_investigator_node_investigator_node_0@{ animation: slow }
```

## Tech stack and Environment

- Python 3.13.5
- `LangChain`
- `LangGraph`
- LLM API
- Management via `uv`

## Project structure

```
project-root/
├── pyproject.toml                      #
├── uv.lock                             # 
├── docker-compose.yml                  #
│
├── src/
│   └── itisamanager/                   # 
│       ├── pyproject.toml              # 
│       ├── Dockerfile                  # 
│       └── src/itisamanager/           # 
│           ├── __init__.py             #
│           ├── main.py                 #
│           ├── config/                 #
│           │   ├── settings.py         # settings
│           │   └── logging_config      # log configuration
│           ├── agent/
│           │   ├── supervisor.py       # supervisor graph
│           │   └── subgraphs/
│           │       ├── investigator.py # investigator subgraph
│           │       ├── synthesizer.py  # synthesizer subgraph
│           │       ├── reviewer.py     # reviewer subgraph
│           │       ├── generator.py    # generator subgraph
│           │       └── writer.py       # writer subgraph
│           └── tools/
│               ├── agent_tool.py       # tools of llm calling
│               ├── utils.py            # varios non-llm utilities
│               └── reader              # file reading utilities
│    
├── mcp-server/                         #
│   ├── pyproject.toml                  #
│   ├── Dockerfile                      #
│   └── src/mcp_server/
│       ├── __init__.py
│       ├── tools/                      # mcp tools
│       │   ├── io_tools.py             # I/O tools
│       │   └── reader.py               # auxiliar functions for io_tools.py
│       ├── config.py                   # mcp configuration
│       ├── main.py                     #
│       └── server.py                   # server
│
└── documents/                          #
```
