import os
import asyncio

from pydantic_ai import Agent, RunContext, UsageLimits
from pydantic_ai.common_tools.tavily import tavily_search_tool, duckduckgo_search_tool
from datetime import date
from src.agent.report_generation_agent import initialize_report_agent
from src.utils.load_utils import BasicConfig

## Initalize the Agent
def generate_root_agent(llm_model, web_search_agent=None, summary_agent=None, report_generation_agent=None, langfuse=None, logger=None):

    root_agent_intructions = root_agent_intructions = "You are a helpful assistant. Use the tools available to you to answer user queries effectively."
    "Use the web search tool to get up-to-date information from the web when needed." \
    "Use the summarize tool to condense lengthy content into concise summaries when appropriate."

    if langfuse:
        root_agent_intructions = langfuse.get_prompt("root_agent_system_prompt").prompt
       

    root_agent = Agent(llm_model, instructions=root_agent_intructions, instrument=True)
    logger.info("Root Base Initialization successful")

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
        
    if report_generation_agent:
        usage_limits = UsageLimits(request_limit=2)  
        @root_agent.tool
        async def generate_final_report(ctx: RunContext[str], content: str) -> str:
            """Use this tool to summarize lengthy content into concise summaries."""
            result = await report_generation_agent.run(content, usage_limits=usage_limits)
            return result.output


    return root_agent

def generate_web_search_agent(llm_model, langfuse=None, logger=None):
     
    web_search_instructions = "You are a web search agent. Use the Web Search tool to perform web searches and provide accurate information based on the search results."
    if langfuse:
        web_search_instructions = langfuse.get_prompt("web_search_agent_system_prompt").prompt
        

    tool = os.getenv('WEB_SEARCH_TOOL', 'tavily')

    if tool != 'tavily':
        web_search_agent = Agent(llm_model, instructions=web_search_instructions, instrument=True,  tools=[duckduckgo_search_tool()])
    
    else:
        # Get API key from environment
        tavily_api_key = os.getenv('TAVILY_API_KEY')
        assert tavily_api_key is not None
        web_search_agent = Agent(llm_model, instructions=web_search_instructions, instrument=True,  tools=[tavily_search_tool(tavily_api_key)])

    @web_search_agent.instructions
    def add_the_date() -> str:  
        return f'The date is {date.today()}.'
    
    return web_search_agent

def generate_summary_agent(llm_model, langfuse=None, logger=None):

    summary_agent_instructions = "Summarize the following content concisely and clearly."
    if langfuse:
        summary_agent_instructions_prompt = langfuse.get_prompt("generate_summary_agent_system_prompt")
        summary_agent_instructions = summary_agent_instructions_prompt.prompt

    summary_agent = Agent(llm_model, instructions=summary_agent_instructions, instrument=True)    
    return summary_agent


def load_all_agents(BasicConfig=None):
    if BasicConfig is None:
        BasicConfig = BasicConfig()

    llm_model, langfuse, logger = BasicConfig.llm_model, BasicConfig.langfuse, BasicConfig.logger
    report_generation_agent = initialize_report_agent(BasicConfig=BasicConfig)

    logger.info("Web Search Agent...")
    web_search_agent = generate_web_search_agent(llm_model=llm_model, langfuse=langfuse, logger=logger)

    logger.info("Initializing Summary Agent...")
    summary_agent = generate_summary_agent(llm_model=llm_model, langfuse=langfuse, logger=logger)

    logger.info("Initializing Root Agent...")
    root_agent = generate_root_agent(llm_model, web_search_agent=web_search_agent, summary_agent=summary_agent, report_generation_agent=report_generation_agent, langfuse=langfuse, logger=logger)
    return root_agent, web_search_agent, summary_agent


def initialize_deep_research_agent(BasicConfig=None):
    if BasicConfig is None:
        BasicConfig = BasicConfig()

    root_agent, web_search_agent, summary_agent = load_all_agents(BasicConfig)
    return root_agent


if __name__ == "__main__":
    try:
        BasicConfig = BasicConfig()
        root_agent = initialize_deep_research_agent(BasicConfig=BasicConfig)
        logger = BasicConfig.logger
        user_request = input("Enter your question: ")
        result = asyncio.run(root_agent.run(user_request))
        print(f"Agent Reply: {result.output}")

    except Exception as e:
        logger.error(f"Startup Failed: {e}")
        exit(1) 

    