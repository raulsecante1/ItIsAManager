from langgraph.graph import StateGraph, START, END

from typing import TypedDict
import logging

import itisamanager.schema as isma
import itisamanager.tools.agent_tools as iagt

logger = logging.getLogger(__name__)


class WriterState(TypedDict):

    finalDraft: isma.FinalDraft | None


def write_file_node(state: WriterState):

    article = state["finalDraft"]
    iagt.write_article(article)
    return {} # terminated


def build_writer_graph():

    writer_builder = StateGraph(WriterState)
    writer_builder.add_node(write_file_node)
    writer_builder.add_edge(START, "write_file_node")
    writer_builder.add_edge("write_file_node", END)

    return writer_builder.compile()
    