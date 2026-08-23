import logging

import itisamanager.agent.agent as iagt

from itisamanager.config.logging_config import setup_logging

setup_logging(logging.DEBUG)

logger = logging.getLogger(__name__)

logger.info("AI Agent started")


prompt = f"""
You are an expert article generation agent.
Now i need you to read the files at "documents/" then generate an article based on it
"""

def main():
    iagt.main_agent_flow(prompt)


if __name__ == "__main__":
    main()
    