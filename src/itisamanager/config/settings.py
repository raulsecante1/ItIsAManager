from langchain_openrouter import ChatOpenRouter

EXTRACTION_MODEL = "deepseek/deepseek-v4-flash-vision-exp" #"~deepseek/deepseek-v4-flash-latest"

EXTRACTION_MODEL_TOKEN_LIMIT = 800000

EXTRACTION_LLM = ChatOpenRouter(
    model = EXTRACTION_MODEL
)

SUB_AGENT_MODEL = "deepseek/deepseek-v4-flash-vision-exp"

SUB_AGENT_MODELL_TOKEN_LIMIT = 800000

MAIN_AGENT_MODEL = "deepseek/deepseek-v4-flash-vision-exp"

MAIN_AGENT_MODELL_TOKEN_LIMIT = 800000