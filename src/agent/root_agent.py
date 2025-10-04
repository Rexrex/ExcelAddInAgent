import os
import dotenv
import logging
import asyncio

from langfuse import get_client, observe
from dotenv import load_dotenv
from pydantic_ai import Agent
from src.utils.load_utils import load_all
from pydantic_ai.common_tools.tavily import tavily_search_tool


## Initalize the Agent
def generate_root_agent(llm_model):
    root_agent_intructions = "You are a helpful assistant. Use the tools available to you to answer user queries effectively."
    root_agent = Agent(llm_model, instructions=root_agent_intructions, instrument=True)
    return root_agent

def generate_web_search_agent(llm_model):
    web_search = "You are a web search agent. Use the Tavily tool to perform web searches and provide accurate information based on the search results."
    # Get API key from environment
    tavily_api_key = os.getenv('TAVILY_API_KEY')
    assert tavily_api_key is not None

    web_search_agent = Agent(llm_model, instructions=web_search, instrument=True,  tools=[tavily_search_tool(tavily_api_key)])
    return web_search_agent

def generate_summary_agent(llm_model):
    summary_agent_instructions = "Summarize the following content concisely and clearly."
    summary_agent = Agent(llm_model, instructions=summary_agent_instructions, instrument=True)    
    return summary_agent


def load_all_agents(llm_model):
    root_agent = generate_root_agent(llm_model)
    web_search_agent = generate_web_search_agent(llm_model)
    summary_agent = generate_summary_agent(llm_model)
    return root_agent, web_search_agent, summary_agent


def initialize_agent():
    llm_model, langfuse, logger = load_all()
    root_agent, web_search_agent, summary_agent = load_all_agents(llm_model)
    return root_agent


if __name__ == "__main__":
    try:
        llm_model, langfuse, logger = load_all()
        root_agent, web_search_agent, summary_agent = load_all_agents(llm_model)

        user_request = input("Enter your question: ")
        result = asyncio.run(web_search_agent.run(user_request))
        print(f"Agent Reply: {result}")

    except Exception as e:
        logger.error(f"Startup Failed: {e}")
        exit(1) 

    