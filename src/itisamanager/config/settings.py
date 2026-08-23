from pathlib import Path
from dotenv import load_dotenv
import os

from langchain_openrouter import ChatOpenRouter
from deepagents.middleware import SubAgentMiddleware
from deepagents.backends import StateBackend
from deepagents import RubricMiddleware

import itisamanager.tools.agent_tools as iagt

###################### API ##########################
load_dotenv()

PROVIDER_API_KEY = os.getenv("PROVIDER_API_KEY")
if not PROVIDER_API_KEY:
    raise ValueError("PROVIDER_API_KEY not found in .env file!")

PROVIDER_BASE_URL = os.getenv("PROVIDER_BASE_URL")

###################### extraction LLM model ##########################

EXTRACTION_MODEL = "deepseek/deepseek-v4-flash-vision-exp" #"~deepseek/deepseek-v4-flash-latest"

EXTRACTION_MODEL_TOKEN_LIMIT = 800000

EXTRACTION_LLM = ChatOpenRouter(
    model = EXTRACTION_MODEL,
    api_key=PROVIDER_API_KEY,
    base_url=PROVIDER_BASE_URL,
)

###################### sub agent #################################

SUB_AGENT_MODEL = "qwen/qwen-plus-2025-07-28:thinking"

SUB_AGENT_MODELL_TOKEN_LIMIT = 800000

SUB_AGENT_PROMPT = """
You are an Investigator Agent specialized in reading local markdown files and extracting structured knowledge from them.

Your primary responsibility is to accept a file path or a directory path from the Master Agent, use the `read_note` tool to read the content, and extract KnowledgeChunk objects.

Guidelines:
1. **Path Handling**: If you receive a directory path, iterate through all `.md` files within it. If you receive a single file path, read only that file.
2. **Tool Usage**: Call the `read_note` tool for each target file.
3. **Data Aggregation**: Each `read_note` call returns a list of `KnowledgeChunk`. You must aggregate all these chunks into a single comprehensive list.
4. **Context Limits**: If the total number of chunks exceeds 15, filter them by relevance (keep the most important ones) and discard the rest to save context for the Master Agent. State this trimming in your final summary.
5. **Artifact Return (Critical)**: In your final response to the Master Agent, you MUST return the aggregated list of `KnowledgeChunk` as a state artifact. Specifically, your final state update must contain a key named `knowledge_chunks` with the list as its value. The Master Agent will retrieve it via `state["knowledge_chunks"]`.
6. **Final Message**: Alongside the artifact, provide a concise human-readable summary (e.g., "Read 3 files, extracted 12 chunks, filtered to the top 10.").

Important: Do not include the raw file content in your final message to the Master Agent. Only the structured KnowledgeChunk list should be passed via the artifact.
"""

SUBAGENT_LLM = ChatOpenRouter(
    model = SUB_AGENT_MODEL,
    api_key=PROVIDER_API_KEY,
    base_url=PROVIDER_BASE_URL,
)

SUBAGENT_MIDDLEWARE = SubAgentMiddleware(
    backend=StateBackend(),
    subagents=[
        {
            "name": "Investigator",
            "description": "Investigate agent",
            "system_prompt": SUB_AGENT_PROMPT,
            "model": SUBAGENT_LLM,
            "tools": [iagt.read_note],
            "api_key": PROVIDER_API_KEY,
            "base_url":PROVIDER_BASE_URL,
        }
    ],
)

###################### main agent ################################

MAIN_AGENT_MODEL = "deepseek/deepseek-v4-flash-vision-exp"

MAIN_AGENT_MODELL_TOKEN_LIMIT = 800000

MAIN_AGENT_LLM = ChatOpenRouter(
    model = MAIN_AGENT_MODEL,
    api_key=PROVIDER_API_KEY,
    base_url=PROVIDER_BASE_URL,
)

######################  path #####################################
PROJECT_ROOT = Path(__file__).parent.parent.parent

ARTICLE_PATH = PROJECT_ROOT / "output" / "generated_article.md"
ARTICLE_PATH.parent.mkdir(parents=True, exist_ok=True)

######################  rubric ###################################

RUBRIC_PROMPT = """
You are an expert editor evaluating a technical article draft.

Evaluate the draft against the following criteria (score each from 1 to 10):
1. Clarity: Is the structure logical? Are paragraphs coherent?
2. Coverage: Does the draft fully cover all the chapters and key_points outlined in the provided ArticleOutline?
"""

RUBRIC_MIDDLEWARE = RubricMiddleware(
    model=MAIN_AGENT_MODEL,
    system_prompt=RUBRIC_PROMPT,
    max_iterations=3,
)