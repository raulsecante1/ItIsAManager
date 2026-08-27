import logging
from typing import TypedDict, List, Annotated
import operator

from langchain.agents import create_agent, AgentState
from langgraph.graph import StateGraph, START

from langchain.agents.middleware import TodoListMiddleware
from deepagents.middleware import SubAgentMiddleware
from deepagents.backends import StateBackend
from langgraph.types import Command

import itisamanager.config.settings as iset
import itisamanager.tools.agent_tools as iagt
import itisamanager.schema as isma
import itisamanager.tools.utils as iutl

logger = logging.getLogger(__name__)

'''class itIsAgentState(AgentState):
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

    return f"Article written on {iset.ARTICLE_PATH}"'''


class AgentState(TypedDict):

    directory_path: str
    knowledge_chunks: Annotated[List[isma.KnowledgeChunk], operator.add]
    chapters: List[isma.Chapter]
    articleOutline: isma.ArticleOutline
    finalDraft: isma.FinalDraft
    score: float
    feedback: str


def investigator_node(state: AgentState) -> dict: 

    file_paths = iagt.list_readable_files(state["directory_path"])
    new_knowledge_chunk = []

    if len(file_paths) < 5:
        for file_path in file_paths:
            new_knowledge_chunk.append(iagt.read_note(file_path))
    else:
        # intellgently choose relative articles to read
        pass

    old_knowledge_chunk = state["knowledge_chunks"]
    combined_knowledge_chunk = old_knowledge_chunk + new_knowledge_chunk

    # intellgently discard similar chunks
    if len(combined_knowledge_chunk) > 20:
        combined_knowledge_chunk = iutl.semantic_deduplicate(combined_knowledge_chunk)

    return {"knowledge_chunks": combined_knowledge_chunk}


def chapter_outline_node(state: AgentState) -> dict:

    knowledge_chunk = state["knowledge_chunks"]
    outline = iagt.synthesize_outline(knowledge_chunk)
    chapter = outline.chapters

    return {"chapter": chapter, "articleOutline": outline}


def article_node(state: AgentState) -> dict:

    outline = state["articleOutline"]
    article = iagt.generate_article(outline)

    return {"finalDraft": article}


def rubirc_node(state: AgentState) -> dict:

    article = state["finalDraft"]
    complete_prompt = f"{iset.RUBRIC_PROMPT}\n\nArticle: \n{article.content}"

    reubric_evaluator = iset.MAIN_AGENT_LLM.with_structured_output(isma.Rubric)

    result = reubric_evaluator.invoke(complete_prompt)

    return {"score": result.score, "feedback": result.feedback}


def rubric_conditional_branch(state: AgentState) -> str:

    rubric_score = state["score"]
    if rubric_score >= 8:
        return "write_file_node"
    elif rubric_score >= 5:
        return "revise_draft_node"
    else:
        return "chapter_outline_node"


def revise_draft_node(state: AgentState) -> dict:

    outline = state["outline"]
    feedback = state["feedback"]
    newdraft = iagt.generate_article(outline, feedback)
    return {"finalDraft": newdraft}


def write_file_node(state: AgentState):

    article = state["finalDraft"]
    iagt.write_article(article)


def main_agent_flow(input: str):

    main_builder = StateGraph(AgentState)
    main_builder.add_node(investigator_node)
    main_builder.add_node(chapter_outline_node)
    main_builder.add_node(article_node)
    main_builder.add_node(rubirc_node)
    main_builder.add_node(revise_draft_node)
    main_builder.add_node(write_file_node)

    main_builder.add_sequence(
        [START, 
         "investigator_node", 
         "chapter_outline_node",
         "article_node",
         "rubirc_node"])
    main_builder.add_conditional_edges("rubirc_node", rubric_conditional_branch)
    main_builder.add_edge("revise_draft_node", "rubirc_node")

    agent_graph = main_builder.compile()
    agent_graph.invoke(input, config={"recursion_limit": 13})  # 3 circles at maximum

