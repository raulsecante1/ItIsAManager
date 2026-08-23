import pathlib
from dotenv import load_dotenv
import os

from langchain_openrouter import ChatOpenRouter
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
    reasoning={
        "effort": "none",
        "exclude": True, 
    },
)

###################### sub agent #################################

SUB_AGENT_MODEL = "qwen/qwen-plus-2025-07-28:thinking"

SUB_AGENT_MODELL_TOKEN_LIMIT = 800000

SUB_AGENT_SYSTEM_PROMPT = """
You are an Investigator Agent specialized in reading local markdown files and extracting structured knowledge from them.

Your primary responsibility is to accept a file path or a directory path from the Master Agent, use the `read_note` tool to read the content, and extract KnowledgeChunk objects.

Guidelines:
1. **Path Handling**: If you receive a directory path, iterate through all `.md` files within it. If you receive a single file path, read only that file.
2. **Tool Usage**: After you get the file list from `list_readable_files`, you MUST call `read_note` with the **exact, unmodified path string** returned by that tool. Do not alter, reconstruct, or correct the path in any way.
3. **Data Aggregation**: Each `read_note` call returns a list of `KnowledgeChunk`. You must aggregate all these chunks into a single comprehensive list.
4. **Context Limits**: If the total number of chunks exceeds 15, filter them by relevance (keep the most important ones) and discard the rest to save context for the Master Agent. State this trimming in your final summary.
5. **Artifact Return (Critical)**: In your final response to the Master Agent, you MUST return the aggregated list of `KnowledgeChunk` as a state artifact. Specifically, your final state update must contain a key named `knowledge_chunks` with the list as its value. The Master Agent will retrieve it via `state["knowledge_chunks"]`.
6. **Final Message**: Alongside the artifact, provide a concise human-readable summary (e.g., "Read 3 files, extracted 12 chunks, filtered to the top 10.").

"""

SUBAGENT_LLM = ChatOpenRouter(
    model = SUB_AGENT_MODEL,
    api_key=PROVIDER_API_KEY,
    base_url=PROVIDER_BASE_URL,
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

MAIN_AGENT_SYSTEM_PROMPT = """
You are a Senior Technical Editor and Research Coordinator.

Your goal is to produce a high-quality, well-structured technical article 
---

## Your Workflow (Recommended Sequence)

1. **Initial Data Collection**  
   - Start by calling `Investigator sub agent` with the root directory provided by the user.  
   - Check the returned message.

2. **Evaluate Sufficiency**  
   - After each batch, assess:    
     * Coverage of key topics relevant to the user's request.  
     * If you see gaps (e.g., missing subtopics), call the `Investigator sub agent` again with a more specific sub-path or a file name pattern.  
   - Stop collecting when you are confident that the material is representative.

3. **Plan the Outline**  
   - Once data is sufficient, call `synthesize_outline`.  
   - Review the returned outline. If it feels incomplete or too shallow, you may go back to step 2 to collect more focused data.

4. **Write the First Draft**  
   - Call `generate_article` to generate the initial draft.  
   - Do not call `write_article` yet.

5. **Handle Rubric Feedback (Automatic)**  
   - The system will automatically evaluate your draft using a Rubric (scoring Clarity and Coverage).  
   - If the score is below 8 in any category, the Rubric system will append a feedback message to your conversation history.  
   - **Read that feedback carefully**, then call `generate_article` again (without changing the outline) – the model will rewrite the article taking the feedback into account.  
   - You may repeat this up to 2–3 times until the score improves.

6. **Finalise**  
   - Once you are satisfied (or the Rubric passes), call `write_article` with the final `FinalDraft` to save it to disk.

---

## Important Decision Rules

- **Do NOT call `write_article` before at least one `FinalDraft` has been produced.**
- **Do NOT call `synthesize_outline` more than once without adding new chunks** – if the outline is weak, collect more data first.
- **Limit your total iterations** – the system will force‑stop after 10 tool calls. Use your judgment to avoid wasteful loops.
- **When calling `Investigator sub agent`, be specific** – if you need more material on a particular topic, mention that in your call to focus on that sub‑folder.

"""

######################  path #####################################
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent.parent

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