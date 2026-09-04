import logging
from typing import TypedDict, Annotated, List
import operator

import itisamanager.schema as isma
import itisamanager.config.settings as iset
import itisamanager.tools.agent_tools as iagt

from langchain.tools import tool
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.messages import ToolMessage


logger = logging.getLogger(__name__)


class InvestigatorState(TypedDict):

    messages: Annotated[list, add_messages]
    directory_path: str
    knowledge_chunks: Annotated[List[isma.KnowledgeChunk], operator.add]


def extract_knowledge_chunk_node(state: InvestigatorState) -> dict:

    all_chunks = []
    for msg in state["messages"]:

        # every tool message with its name in read_file and has file content
        if isinstance(msg, ToolMessage) and msg.name == "read_file":

            file_content = msg.content
            if isinstance(file_content, list):
                # tool message has format [{"type": "text", "text": "..."}]
                texts = [block.get("text", "") for block in file_content if block.get("type") == "text"]
                file_content = "\n".join(texts)
            
            if msg.status == "error":
                logger.error(f"reading failed: {file_content}")
                continue
            
            chunks_obj = iagt.read_note(file_content)
            all_chunks.extend(chunks_obj.knowledge_chunk)
            
    return {"knowledge_chunks": all_chunks}


async def build_investigator_subgraph():

    client = MultiServerMCPClient({
        "filesystem": {
            "transport": "http", # according to the type
            "url": iset.MCP_URL, # http://localhost:8000/mcp
        }
    })
    mcp_tools = await client.get_tools()

    def llm_decide(state: InvestigatorState):
        llm_with_tools = iset.MAIN_AGENT_LLM.bind_tools(mcp_tools)
        system_msg = {
            "role": "system",
            "content": (
                "You are a file reader agent. Use list_readable_files and read_file to read files. "
                "After reading all files, say 'I have finished reading all files.' and stop calling tools."
            )
        }
        messages = [system_msg] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(InvestigatorState)
    builder.add_node("decide", llm_decide)
    builder.add_node("tools", ToolNode(mcp_tools))
    builder.add_node(extract_knowledge_chunk_node)
    
    builder.add_edge(START, "decide")
    builder.add_conditional_edges("decide", tools_condition, {"tools": "tools", END: "extract_knowledge_chunk_node"})
    builder.add_edge("tools", "decide")
    builder.add_edge("extract_knowledge_chunk_node", END)
    
    return builder.compile()