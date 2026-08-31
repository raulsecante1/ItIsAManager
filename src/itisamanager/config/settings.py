import pathlib
from dotenv import load_dotenv
import os

from langchain_openrouter import ChatOpenRouter


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
    reasoning={
        "effort": "none",
        "exclude": True, 
    },
)

###################### main agent ################################

MAIN_AGENT_MODEL = "deepseek/deepseek-v4-flash-vision-exp"

MAIN_AGENT_MODELL_TOKEN_LIMIT = 800000

MAIN_AGENT_LLM = ChatOpenRouter(
    model = MAIN_AGENT_MODEL,
    api_key=PROVIDER_API_KEY,
    base_url=PROVIDER_BASE_URL,
    reasoning={
        "effort": "none",
        "exclude": True, 
    },
)

######################  path #####################################
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent.parent

ARTICLE_PATH = PROJECT_ROOT / "output" / "generated_article.md"
ARTICLE_PATH.parent.mkdir(parents=True, exist_ok=True)

######################  file/chunk ###############################

SELECT_THRESHOLD = 5 # how many file to read
TOP_K = SELECT_THRESHOLD # how many similiar files to consider during the file selection
FILE_RELEVANCE_THRESHOLD = 0.1 # discard those has relevance lower than this value with the user query even selected
CHUNK_SEMANTIC_THRESHOLD = 0.85 # discard chunks that has similarity higher than this value
MAXIMUM_CHUNK = 20 # maximum chunk to have for outline generation

######################  rubric ###################################

RUBRIC_PROMPT = """
You are an expert editor evaluating a technical article draft.

Evaluate the draft against the following criteria (score each from 1 to 10 then yeild a weighed score):
1. Clarity: Is the structure logical? Are paragraphs coherent?
2. Coverage: Does the draft fully cover all the chapters and key_points outlined in the provided ArticleOutline?
3. max 300 words
"""

######################  embedding model ##########################

EMBEDDING_MODEL = None

def get_EMBEDDING_MODEL():
    global EMBEDDING_MODEL
    if EMBEDDING_MODEL is None:
        from sentence_transformers import SentenceTransformer
        EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2") # "all-MiniLM-L6-v2" converts text into 384-dimensional vectors.
    return EMBEDDING_MODEL

######################  MCP url ##################################

MCP_URL = "http://localhost:8000/mcp"