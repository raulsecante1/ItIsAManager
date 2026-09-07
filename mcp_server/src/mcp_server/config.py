############################## file path ####################################
import pathlib
import os

OUTPUT_DIR = pathlib.Path(os.getenv("MCP_OUTPUT_DIR", "/app/output")).resolve()
DOCS_DIR = pathlib.Path(os.getenv("MCP_DOCS_DIR", "/app/documents")).resolve()

############################## embedding model ####################################

from enum import StrEnum

class RerankerType(StrEnum):
    CROSS_ENCODER = "CrossEncoder"
    TRAINED_MODEL = "Trained model"
    SBERT = "SBERT"

TOP_K = 5
RERANKER = {"type": RerankerType.CROSS_ENCODER, "model": "model.pt"}