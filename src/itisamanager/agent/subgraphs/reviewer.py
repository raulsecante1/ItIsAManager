from langgraph.graph import StateGraph, START, END, add_messages

from typing import TypedDict, Annotated
import logging

import itisamanager.schema as isma
import itisamanager.config.settings as iset

logger = logging.getLogger(__name__)


class RubricState(TypedDict):

    articleOutline: isma.ArticleOutline | None
    finalDraft: isma.FinalDraft | None
    messages: Annotated[list, add_messages]
    score: float
    feedback: str


def rubirc_node(state: RubricState) -> dict:

    article = state["finalDraft"]
    user_messages = [
        message
        for message in state["messages"]
        if message.type == "human"
    ]

    query = user_messages[-1].content if user_messages else None

    complete_prompt = f"{iset.RUBRIC_PROMPT}\n\nArticle: \n{article.content}" + (f"\n\nUser query: {query}" if query else "")

    reubric_evaluator = iset.MAIN_AGENT_LLM.with_structured_output(isma.Rubric)

    result = reubric_evaluator.invoke(complete_prompt)

    return {"score": result.score, "feedback": result.feedback}


def rubric_conditional_branch(state: RubricState) -> str:

    rubric_score = state["score"]
    if rubric_score >= 8:
        return "write"
    elif rubric_score >= 5:
        return "revise"
    else:
        return "outline"


def build_rubric_graph():

    rubric_builder = StateGraph(RubricState)
    rubric_builder.add_node(rubirc_node)
    rubric_builder.add_edge(START, "rubirc_node")
    rubric_builder.add_edge("rubirc_node", END)

    return rubric_builder.compile()