import logging

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import TodoListMiddleware
from deepagents.middleware import SubAgentMiddleware
from deepagents.backends import StateBackend

import itisamanager.config.settings as iset
import itisamanager.tools.agent_tools as iagt
import itisamanager.schema as isma

logger = logging.getLogger(__name__)

class itIsAgentState(AgentState):
    knowledge_chunks: isma.KnowledgeChunks

SUBAGENT_MIDDLEWARE = SubAgentMiddleware(
    backend=StateBackend(),
    subagents=[
        {
            "name": "Investigator sub agent",
            "description": "Investigate agent",
            "system_prompt": iset.SUB_AGENT_SYSTEM_PROMPT,
            "model": iset.SUBAGENT_LLM,
            "tools": [iagt.read_note,
                      iagt.list_readable_files,
                      iagt.generate_article,
            ],
            "api_key": iset.PROVIDER_API_KEY,
            "base_url": iset.PROVIDER_BASE_URL,
        }
    ],
    state_schema=itIsAgentState,
)


def create_main_agent():
    """
    create the main agent
    """
    return create_agent(
        name="Main agnet",
        model=iset.MAIN_AGENT_LLM, 
        tools=[iagt.write_article, iagt.synthesize_outline], 
        middleware=[
            SUBAGENT_MIDDLEWARE, 
            iset.RUBRIC_MIDDLEWARE, 
            TodoListMiddleware(),
        ],
        state_schema=itIsAgentState,
    )




def main_agent_flow(user_query: str):
    """
    the main agent workflow
    """
    main_agent = create_main_agent()
    state = main_agent.invoke({"messages": [{"role": "user", "content": user_query}]})

    '''
    knowledge_chunks = state.get("knowledge_chunks", [])
    
    if not knowledge_chunks:
        raise ValueError("No knowledge chunks extracted. Check file paths.")

    outline = synthesize_outline(knowledge_chunks)
    final_article = generate_article(outline)

    main_agent.invoke({
        "messages": [{"role": "user", "content": f"Write down the following article to disk{final_article.content}"}],
    })
    '''

    return f"Article written on {iset.ARTICLE_PATH}"
