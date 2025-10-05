import os
import dotenv
import logging
import asyncio

from src.utils.load_utils import BasicConfig
from pydantic_ai import Agent, RunContext, UsageLimits
from pydantic import BaseModel

class FinalReport(BaseModel):
    report: str
    next_steps: str
    agent_actions: str



## Initalize the Agent
def generate_report_agent(llm_model, langfuse=None, logger=None):
    final_report_agent_intructions = "Your task is to create executive summaries and detailed reports based on the data provided. The data comes from assembly of different agents." \

    if langfuse:
        final_report_agent_prompt = langfuse.get_prompt("final_report_agent_system_prompt")
        if final_report_agent_prompt:
             final_report_agent_intructions = final_report_agent_prompt.prompt
       
    final_report_agent = Agent(llm_model, instructions=final_report_agent_intructions, instrument=True)
    logger.info("Final Report Agent Initialization successful")

    return final_report_agent



def initialize_report_agent(BasicConfig=None):
    if( BasicConfig is None):
        BasicConfig = BasicConfig()
    llm_model, langfuse, logger = BasicConfig.llm_model, BasicConfig.langfuse, BasicConfig.logger
    logger.info("Initializing Excel Agent...")
    final_report_agent = generate_report_agent(llm_model, langfuse=langfuse, logger=logger)
    return final_report_agent


if __name__ == "__main__":
    try:
        BasicConfig = BasicConfig()
        rooting_agent = initialize_report_agent(BasicConfig=BasicConfig)
        logger = BasicConfig.logger
        user_request = input("Enter your question for the Final Report agent: ")
        result = asyncio.run(rooting_agent.run(user_request))
        print(f"Agent Reply: {result.output}")

    except Exception as e:
        logger.error(f"Startup Failed: {e}")
        exit(1) 

    