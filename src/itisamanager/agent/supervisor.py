from langchain.messages import HumanMessage
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.checkpoint.memory import MemorySaver

import itisamanager.schema as isma
import itisamanager.agent.subgraphs as iasb

import logging
from typing import TypedDict, List, Annotated
import operator

logger = logging.getLogger(__name__)


class SupervisorState(TypedDict):

    messages: Annotated[list, add_messages]
    directory_path: str
    knowledge_chunks: Annotated[List[isma.KnowledgeChunk], operator.add]
    articleOutline: isma.ArticleOutline | None
    finalDraft: isma.FinalDraft | None
    score: float
    feedback: str
    iteration: int = 3


def rubric_conditional_branch(state: SupervisorState) -> str:

    rubric_score = state["score"]

    if rubric_score >= 8:
        logger.info(f"score {rubric_score} >= 8, write into file")
        return "write"
    elif rubric_score >= 5:
        logger.info(f"score {rubric_score} between 5, 8 regenerate the article according to the feedback")
        return "revise"
    else:
        logger.info(f"score {rubric_score} < 5, rewrite the outline")
        return "outline"


def build_supervisor_graph():

    supervisor_builder = StateGraph(SupervisorState)
    supervisor_builder.add_node("investigator", iasb.investigator.build_investigator_graph())
    supervisor_builder.add_node("synthesizer", iasb.synthesizer.build_synthesizer_graph())
    supervisor_builder.add_node("generator", iasb.generator.build_article_graph())
    supervisor_builder.add_node("reviewer", iasb.reviewer.build_rubric_graph())
    supervisor_builder.add_node("writer", iasb.writer.build_writer_graph())

    supervisor_builder.add_edge(START, "investigator")
    supervisor_builder.add_edge("investigator", "synthesizer")
    supervisor_builder.add_edge("synthesizer", "generator")
    supervisor_builder.add_edge("generator", "reviewer")

    supervisor_builder.add_conditional_edges(
        "reviewer", 
        rubric_conditional_branch, 
        {
            "write": "writer",
            "revise": "generator",
            "outline": "synthesizer"
            }
    )

    supervisor_builder.add_edge("writer", END)

    return supervisor_builder.compile(checkpointer=MemorySaver())