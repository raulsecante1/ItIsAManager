from langchain.agents import create_agent

import itisamanager.config.settings as iset
import src.itisamanager.tools.agent_tools as iagt

main_agent = create_agent(model=iset.MAIN_AGENT_MODEL, tools=[iagt.write_article])

sub_agent = create_agent(model=iset.SUB_AGENT_MODEL, tools=[iagt.read_note])