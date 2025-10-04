import os
import dotenv
import logging
import asyncio

from langfuse import get_client, observe
from dotenv import load_dotenv
from pydantic_ai import Agent
from src.utils.load_utils import load_all


## Initalize the Agent
class BaseAgent():
    agent = None
    langfuse = None
    
    def __init__(self, instructions, llm_model, langfuse, logger=None):

        self.agent = Agent(llm_model, instructions=instructions, instrument=True)
        if logger:
           logger.info("Agent Setup successful")

    @observe()
    async def run(self, input):
        print(f"llm_chat input: {input}")
        result = await self.agent.run(input)  
        output = result.output
    
        langfuse.update_current_trace(
            input=input,
            output=output
        )
    
        return output

if __name__ == "__main__":
    try:
        llm_model, langfuse, logger = load_all()
        instructions = "Your are the Root Agent. Be Concise. Answer the question as best as you can."
        simple_agent = BaseAgent(llm_model=llm_model, langfuse=langfuse, instructions=None, logger=logger)
        chef_agent = Agent(llm_model, instructions="Your are a chef in a 3 star Michelin hotel", instrument=True)
        user_request = input("Enter your question: ")
        result = asyncio.run(simple_agent.run(user_request))
        print(f"Agent Reply: {result}")

        user_chef_request = input("Enter your cooking question: ")
        result = asyncio.run(chef_agent.run(user_chef_request)) 
        print(f"Chef Agent Reply: {result}")

    except Exception as e:
        logger.error(f"Startup Failed: {e}")
        exit(1) 

    