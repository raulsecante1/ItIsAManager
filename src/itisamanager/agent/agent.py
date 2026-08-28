import logging
from typing import TypedDict, List, Annotated
import operator

from langchain.agents import AgentState
from langgraph.graph import StateGraph, START, END, add_messages
from langchain.messages import HumanMessage

import itisamanager.config.settings as iset
import itisamanager.tools.agent_tools as iagt
import itisamanager.schema as isma
import itisamanager.tools.utils as iutl

logger = logging.getLogger(__name__)


class AgentState(TypedDict):

    messages: Annotated[list, add_messages]
    directory_path: str
    knowledge_chunks: Annotated[List[isma.KnowledgeChunk], operator.add]
    articleOutline: isma.ArticleOutline | None
    finalDraft: isma.FinalDraft | None
    score: float
    feedback: str


def investigator_node(state: AgentState) -> dict: 

    file_dict = iagt.list_readable_files(state["directory_path"])
    file_paths = [file for files in file_dict.values() for file in files]
    new_knowledge_chunk = []

    user_query = ""
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            user_query = msg.content
            break
     
    if len(file_paths) > iset.SELECT_THRESHOLD:
        file_paths = iutl.select_relevant_files(file_paths, user_query, top_k=iset.TOP_K,threshold=iset.FILE_RELEVANCE_THRESHOLD) # select the top K most related files

    for file_path in file_paths:
        chunks_obj = iagt.read_note(file_path)
        new_knowledge_chunk.extend(chunks_obj.knowledge_chunk)

    old_knowledge_chunk = state["knowledge_chunks"]
    combined_knowledge_chunk = old_knowledge_chunk + new_knowledge_chunk

    # intellgently discard similar chunks
    if len(combined_knowledge_chunk) > iset.MAXIMUM_CHUNK:
        combined_knowledge_chunk = iutl.semantic_deduplicate(combined_knowledge_chunk, threshold=iset.CHUNK_SEMANTIC_THRESHOLD)

    return {"knowledge_chunks": combined_knowledge_chunk}


def outline_node(state: AgentState) -> dict:

    knowledge_chunk = state["knowledge_chunks"]
    outline = iagt.synthesize_outline(knowledge_chunk)
    chapter = outline.chapters

    return {"articleOutline": outline}


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
        return "write"
    elif rubric_score >= 5:
        return "revise"
    else:
        return "outline"


def revise_draft_node(state: AgentState) -> dict:

    outline = state["articleOutline"]
    feedback = state["feedback"]
    newdraft = iagt.generate_article(outline, feedback)
    return {"finalDraft": newdraft}


def write_file_node(state: AgentState):

    article = state["finalDraft"]
    iagt.write_article(article)
    return {} # terminated


def main_agent_flow(user_query: str, dir_path: str):

    main_builder = StateGraph(AgentState)
    main_builder.add_node(investigator_node)
    main_builder.add_node(outline_node)
    main_builder.add_node(article_node)
    main_builder.add_node(rubirc_node)
    main_builder.add_node(revise_draft_node)
    main_builder.add_node(write_file_node)

    '''
    main_builder.add_sequence(
        [START, 
         "investigator_node", 
         "outline_node",
         "article_node",
         "rubirc_node"])
    '''
    main_builder.add_edge(START, "investigator_node")
    main_builder.add_edge("investigator_node", "outline_node")
    main_builder.add_edge("outline_node", "article_node")
    main_builder.add_edge("article_node", "rubirc_node")
    main_builder.add_conditional_edges(
        "rubirc_node", 
        rubric_conditional_branch, 
        {
            "write": "write_file_node",
            "revise": "revise_draft_node",
            "outline": "outline_node"
            }
    )
    main_builder.add_edge("revise_draft_node", "rubirc_node")
    main_builder.add_edge("write_file_node", END)

    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "directory_path": dir_path,
        "knowledge_chunks": [],
        "articleOutline": None,
        "finalDraft": None,
        "score": 0.0,
        "feedback": "",
    }

    agent_graph = main_builder.compile()
    agent_graph.invoke(initial_state, config={"recursion_limit": 13})  # 3 circles at maximum

    print(agent_graph.get_graph().draw_mermaid()) # get the mermaid chart of the graph

    return f"Article written at {iset.ARTICLE_PATH.parent}"

