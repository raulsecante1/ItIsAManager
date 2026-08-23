import logging

import itisamanager.agent.agent as iage

import itisamanager.tools.utils as iutl
import itisamanager.config.settings as iset
import pathlib

from itisamanager.config.logging_config import setup_logging

setup_logging(logging.INFO)

logger = logging.getLogger(__name__)

logger.info("AI Agent started")


prompt = f"""
You are an expert article generation agent.
Now i need you to read the files at "documents/" then generate an article based on it
"""

def main():
    iage.main_agent_flow(prompt)

    '''
    print (f"\n CWD is {iset.PROJECT_ROOT}")
    print(f"\n documents/LangChain_core_components_model.md exists? {pathlib.Path("documents/LangChain_core_components_model.md").exists()}")
    a = iutl.read_file("documents/LangChain_core_components_model.md")
    print(a.source)
    print("---------------------")
    print(a.content[:50])
    '''


if __name__ == "__main__":
    main()
    