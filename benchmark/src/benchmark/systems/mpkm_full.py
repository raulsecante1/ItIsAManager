import benchmark.systems.schema as bsma
import benchmark.config as bcfg
import itisamanager.agent.supervisor as sias
import itisamanager.config.settings as sics

from langsmith import Client

import logging
import time
import asyncio

logger = logging.getLogger(__name__)


def mpkm_call(user_query: str) -> bsma.SystemOutput:
    return asyncio.run(aux_mpkm_call(user_query))


async def aux_mpkm_call(user_query: str) -> bsma.SystemOutput:

    initial_state = {
        "messages": [("user", user_query)],
        "directory_path": str(sics.PROJECT_ROOT / "documents"),
        "knowledge_chunks": [],
        "articleOutline": None,
        "finalDraft": None,
        "score": 0.0,
        "feedback": "",
    }
    config = {
        "recursion_limit": 16,  # 13 steps = 3 circles at maximum, plus 3 auto retries
        "configurable": {
            "thread_id": "1"
        }
    }

    start = time.perf_counter()
    agent_graph = await sias.build_supervisor_graph()
    final_state = await agent_graph.ainvoke(initial_state, config=config)
    elapsed  = time.perf_counter() - start
    '''
    client = Client()

    run = client.read_run(
        bcfg.THIS_LANGSMITH_RUN_ID,
        load_child_runs=True,
    )'''

    final_draft = final_state.get("finalDraft")

    structured_result = bsma.SystemOutput(
        article = final_draft.content if final_draft else "",
        latency=elapsed,
        token_usage=0#run.total_tokens
    )

    return structured_result
