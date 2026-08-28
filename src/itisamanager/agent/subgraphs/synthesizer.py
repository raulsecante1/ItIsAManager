import logging
from typing import TypedDict, Annotated, List
import operator

import itisamanager.schema as isma
import itisamanager.tools.agent_tools as iagt

from langgraph.graph import StateGraph, START, END


logger = logging.getLogger(__name__)


class SynthesizerState(TypedDict):

    knowledge_chunks: Annotated[List[isma.KnowledgeChunk], operator.add]
    articleOutline: isma.ArticleOutline | None


def outline_node(state: SynthesizerState) -> dict:

    knowledge_chunk = state["knowledge_chunks"]
    outline = iagt.synthesize_outline(knowledge_chunk)


    return {"articleOutline": outline}


def build_synthesizer_graph():

    synthesizer_builder = StateGraph(SynthesizerState)
    synthesizer_builder.add_node(outline_node)
    synthesizer_builder.add_edge(START, "outline_node")
    synthesizer_builder.add_edge("outline_node", END)
    synthesizer_graph = synthesizer_builder.compile()

    return synthesizer_graph


