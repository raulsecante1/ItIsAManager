import logging

import itisamanager.config.settings as iset
import itisamanager.agent.supervisor as iasp
from itisamanager.config.logging_config import setup_logging

setup_logging(logging.INFO)

logger = logging.getLogger(__name__)

logger.info("AI Agent started")


prompt = f"""
You are an expert article generation agent.
Now i need you to read the files at "documents/" then generate an article based on it
"""


def main():
    initial_state = {
        "messages": [("user", "read the files at documents/ and generate an article based on that")],
        "directory_path": str(iset.PROJECT_ROOT / "documents"),
        "knowledge_chunks": [],
        "articleOutline": None,
        "finalDraft": None,
        "score": 0.0,
        "feedback": "",
    }
    config = {
        "recursion_limit": 13,  # 3 circles at maximum
        "configurable": {
            "thread_id": "1"
        }
    }

    agent_graph = iasp.build_supervisor_graph()
    final_state = agent_graph.invoke(initial_state, config=config)

    logger.info("Finished: ")
    logger.info(f"outline: {final_state.get('articleOutline')}")
    logger.info(f"final draft (first 100 characters): {final_state.get('finalDraft', {}).content[:100] if final_state.get('finalDraft') else '无'}")
    logger.info(f"score: {final_state.get('score')}")

    print(f"mermaid chart: \n{agent_graph.get_graph().draw_mermaid()}")


if __name__ == "__main__":
    main()
    