from langgraph.graph import StateGraph, START, END, add_messages

from typing import TypedDict, Annotated
import logging
import operator

import itisamanager.schema as isma
import itisamanager.tools.agent_tools as iagt

logger = logging.getLogger(__name__)


class ArticleState(TypedDict):

    articleOutline: isma.ArticleOutline | None
    finalDraft: isma.FinalDraft | None
    messages: Annotated[list, add_messages]
    knowledge_chunks: Annotated[list[isma.KnowledgeChunk], operator.add]


def article_node(state: ArticleState, feedback: str | None = None) -> dict:

    outline = state["articleOutline"]
    user_messages = [
        message
        for message in state["messages"]
        if message.type == "human"
    ]
    all_chunks = state["knowledge_chunks"]

    
    query = user_messages[-1].content if user_messages else None

    article = iagt.generate_article(all_chunks=all_chunks, outline=outline, feedback=feedback, user_query=query)

    return {"finalDraft": article}


def build_article_graph():

    article_builder = StateGraph(ArticleState)
    article_builder.add_node(article_node)
    article_builder.add_edge(START, "article_node")
    article_builder.add_edge("article_node", END)

    return article_builder.compile()
    