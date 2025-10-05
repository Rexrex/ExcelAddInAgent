
import asyncio

from langfuse import get_client, observe
from dotenv import load_dotenv
from pydantic_ai import Agent


## Initalize the Agent
class BaseAgent():
    agent = None
    langfuse = None
    tools = None
    
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
        instructions = "Be Concise. Answer the question as best as you can."
        simple_agent = BaseAgent(llm_model=llm_model, langfuse=langfuse, instructions=None, logger=logger)
        user_request = input("Enter your question: ")
        result = asyncio.run(simple_agent.run(user_request))
        print(f"Agent Reply: {result}")

    except Exception as e:
        logger.error(f"Startup Failed: {e}")
        exit(1) 

    