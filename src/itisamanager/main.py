import logging

import itisamanager.agent.agent as iage

import itisamanager.config.settings as iset

from itisamanager.config.logging_config import setup_logging

setup_logging(logging.INFO)

logger = logging.getLogger(__name__)

logger.info("AI Agent started")


prompt = f"""
You are an expert article generation agent.
Now i need you to read the files at "documents/" then generate an article based on it
"""


def main():
    iage.main_agent_flow(user_query=prompt,dir_path=str(iset.PROJECT_ROOT / "documents"))


if __name__ == "__main__":
    main()
    