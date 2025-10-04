import os
import dotenv
import logging
import asyncio

from langfuse import get_client, observe
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext, UsageLimits
from src.utils.load_utils import load_all
from pydantic_ai.common_tools.tavily import tavily_search_tool
from dataclasses import dataclass
from datetime import date


@dataclass
class Topic:  
    topic: str

## Initalize the Agent
def generate_root_agent(llm_model, web_search_agent=None, summary_agent=None, langfuse=None, logger=None):

    root_agent_intructions = ""
    if langfuse:
        root_agent_intructions = langfuse.get_prompt("root_agent_system_prompt")
    else:
        root_agent_intructions = "You are a helpful assistant. Use the tools available to you to answer user queries effectively." \
    "Use the web search tool to get up-to-date information from the web when needed." \
    "Use the summarize tool to condense lengthy content into concise summaries when appropriate."

    root_agent = Agent(llm_model, instructions=root_agent_intructions.prompt, instrument=True)

    if web_search_agent:
        usage_limits = UsageLimits(request_limit=2)  
        @root_agent.tool
        async def web_search(ctx: RunContext[str], query: str) -> str:
            """Use this tool to perform web searches and retrieve up-to-date information from the web."""
            result = await web_search_agent.run(query, usage_limits=usage_limits)
            return result.output
    
    if summary_agent:
        @root_agent.tool
        async def summarize(ctx: RunContext[str], content: str) -> str:
            """Use this tool to summarize lengthy content into concise summaries."""
            result = await summary_agent.run(content)
            return result.output

    return root_agent

def generate_web_search_agent(llm_model, langfuse=None, logger=None):
     
    web_search_instructions = ""
    if langfuse:
        web_search_instructions = langfuse.get_prompt("web_search_agent_system_prompt")
    else:
        web_search_instructions = "You are a web search agent. Use the Tavily tool to perform web searches and provide accurate information based on the search results."
    # Get API key from environment
    tavily_api_key = os.getenv('TAVILY_API_KEY')
    assert tavily_api_key is not None

    web_search_agent = Agent(llm_model, instructions=web_search_instructions.prompt, instrument=True,  tools=[tavily_search_tool(tavily_api_key)])

    @web_search_agent.instructions
    def add_the_date() -> str:  
        return f'The date is {date.today()}.'
    
    return web_search_agent

def generate_summary_agent(llm_model, langfuse=None, logger=None):

    summary_agent_instructions = ""
    if langfuse:
        summary_agent_instructions = langfuse.get_prompt("generate_summary_agent_system_prompt")
    else:
        summary_agent_instructions = "Summarize the following content concisely and clearly."

    summary_agent = Agent(llm_model, instructions=summary_agent_instructions.prompt, instrument=True)    
    return summary_agent


def load_all_agents(llm_model, langfuse, logger):
    logger.info("Web Search Agent...")
    web_search_agent = generate_web_search_agent(llm_model=llm_model, langfuse=langfuse, logger=logger)
    logger.info("Initializing Summary Agent...")
    summary_agent = generate_summary_agent(llm_model=llm_model, langfuse=langfuse, logger=logger)
    logger.info("Initializing Root Agent...")
    root_agent = generate_root_agent(llm_model, web_search_agent=web_search_agent, summary_agent=summary_agent, langfuse=langfuse, logger=logger)
    return root_agent, web_search_agent, summary_agent


def initialize_agent():
    llm_model, langfuse, logger = load_all()
    logger.info("Initializing Agents...")
    root_agent, web_search_agent, summary_agent = load_all_agents(llm_model, langfuse, logger)
    return root_agent


if __name__ == "__main__":
    try:
        llm_model, langfuse, logger = load_all()
        root_agent, web_search_agent, summary_agent = load_all_agents(llm_model, langfuse)

        user_request = input("Enter your question: ")
        result = asyncio.run(root_agent.run(user_request))
        print(f"Agent Reply: {result.output}")

    except Exception as e:
        logger.error(f"Startup Failed: {e}")
        exit(1) 

    