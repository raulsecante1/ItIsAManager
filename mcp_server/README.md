# MCP server

## What it is ?

An independent MCP server project for the itIsAManager project

## Sub project structure
```
project-root/
├── ...                                 #
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

## Install

There are 2 ways to install manually via `docker build -t <container-name> . ` to install the mcp as a container then `docker run -d -p port:port --name <image-name> <container-name>`, or just use `docker-compose.yaml` via `docker compose up`.

But on both way you might need to specify the port.