from dotenv import load_dotenv
import os
import pathlib

from langchain_openrouter import ChatOpenRouter

load_dotenv()

############################## API ##############################
PROVIDER_API_KEY = os.getenv("PROVIDER_API_KEY")
if not PROVIDER_API_KEY:
    raise ValueError("PROVIDER_API_KEY not found in .env file!")

PROVIDER_BASE_URL = os.getenv("PROVIDER_BASE_URL")


############################## LangSmith ##############################
THIS_LANGSMITH_RUN_ID = os.getenv("THIS_LANGSMITH_RUN_ID")


############################## Judger Model ##############################
JUDGER_MODEL = "deepseek/deepseek-v4-flash-vision-exp"

JUDGER_MODEL_TOKEN_LIMIT = 800000

JUDGER_LLM = ChatOpenRouter(
    model = JUDGER_MODEL,
    api_key=PROVIDER_API_KEY,
    base_url=PROVIDER_BASE_URL,
    reasoning={
        "effort": "none",
        "exclude": True, 
    },
)

############################## Path ##############################
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent