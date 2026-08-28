import logging
from typing import TypedDict, Annotated, List
import operator

import itisamanager.schema as isma
import itisamanager.tools.agent_tools as iagt
import itisamanager.tools.utils as iutl
import itisamanager.config.settings as iset

from langgraph.graph import StateGraph, START, END, add_messages
from langchain.messages import HumanMessage


logger = logging.getLogger(__name__)


class InvestigatorState(TypedDict):

    messages: Annotated[list, add_messages]
    directory_path: str
    knowledge_chunks: Annotated[List[isma.KnowledgeChunk], operator.add]



def investigator_node(state: InvestigatorState) -> dict: 

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


def build_investigator_graph():

    investigator_buildr = StateGraph(InvestigatorState)
    investigator_buildr.add_node(investigator_node)

    investigator_buildr.add_edge(START, "investigator_node")
    investigator_buildr.add_edge("investigator_node", END)

    return investigator_buildr.compile()