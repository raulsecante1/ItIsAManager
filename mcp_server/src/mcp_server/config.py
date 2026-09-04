import pathlib
import os

OUTPUT_DIR = pathlib.Path(os.getenv("MCP_OUTPUT_DIR", "/app/output")).resolve()
DOCS_DIR = pathlib.Path(os.getenv("MCP_DOCS_DIR", "/app/documents")).resolve()