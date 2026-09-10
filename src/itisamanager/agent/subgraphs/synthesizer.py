import logging
from typing import TypedDict, Annotated
import operator

import itisamanager.schema as isma
import itisamanager.tools.agent_tools as iagt

from langgraph.graph import StateGraph, START, END, add_messages


logger = logging.getLogger(__name__)


class SynthesizerState(TypedDict):

    knowledge_chunks: Annotated[list[isma.KnowledgeChunk], operator.add]
    articleOutline: isma.ArticleOutline | None
    messages: Annotated[list, add_messages]


def outline_node(state: SynthesizerState) -> dict:

    knowledge_chunk = state["knowledge_chunks"]
    user_messages = [
        message
        for message in state["messages"]
        if message.type == "human"
    ]

    query = user_messages[-1].content if user_messages else None

    outline = iagt.synthesize_outline(knowledge_chunk, query)


    return {"articleOutline": outline}


def build_synthesizer_graph():

    synthesizer_builder = StateGraph(SynthesizerState)
    synthesizer_builder.add_node(outline_node)
    synthesizer_builder.add_edge(START, "outline_node")
    synthesizer_builder.add_edge("outline_node", END)
    synthesizer_graph = synthesizer_builder.compile()

    return synthesizer_graph


