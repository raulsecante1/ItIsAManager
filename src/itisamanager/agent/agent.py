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

