from langgraph.graph import StateGraph, START, END

from typing import TypedDict
import logging

import itisamanager.schema as isma
import itisamanager.tools.agent_tools as iagt

logger = logging.getLogger(__name__)


class ArticleState(TypedDict):

    articleOutline: isma.ArticleOutline | None
    finalDraft: isma.FinalDraft | None


def article_node(state: ArticleState, feedback: str | None = None) -> dict:

    outline = state["articleOutline"]
    article = iagt.generate_article(outline, feedback=feedback)

    return {"finalDraft": article}


def build_article_graph():

    article_builder = StateGraph(ArticleState)
    article_builder.add_node(article_node)
    article_builder.add_edge(START, "article_node")
    article_builder.add_edge("article_node", END)

    return article_builder.compile()
    