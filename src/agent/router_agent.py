
import asyncio

from pydantic_ai import Agent, RunContext, UsageLimits
from src.agent.excel_agent import initialize_excel_agent
from src.agent.research_agent import initialize_deep_research_agent
from src.utils.load_utils import BasicConfig

## Initalize the Agent
def generate_routing_agent(llm_model, research_agent=None, excel_agent=None, langfuse=None, logger=None):

    routing_agent_intructions = "You are the first line regarding a user request. Evaluate where the request should be redirected based on the content of the request." \
    "You have 2 different tools. A deep research agent. And an excel agent that can help with excel related tasks." \
    "If the request is related to excel, or data analysis, or anything that can be done in excel, redirect the request to the excel agent." \
    "If the request is related to research, or general questions, or anything that requires looking up information, redirect the request to the research agent." \

    if langfuse:
        routing_agent_prompt = langfuse.get_prompt("rooting_agent_system_prompt")
        if routing_agent_prompt:
             routing_agent_intructions = routing_agent_prompt.prompt
       

    rooting_agent = Agent(llm_model, instructions=routing_agent_intructions, instrument=True)
    logger.info("Routing Base Initialization successful")

    if research_agent:
        usage_limits = UsageLimits(request_limit=5)  
        @rooting_agent.tool
        async def deep_research(ctx: RunContext[str], query: str) -> str:
            """Use this tool to perform deep research calls."""
            result = await research_agent.run(query, usage_limits=usage_limits, message_history=ctx.messages)
            return result.output
    
    if excel_agent:
        @rooting_agent.tool
        async def excel_queries(ctx: RunContext[str], content: str) -> str:
            """Use this tool to handle excel specific queries."""
            result = await excel_agent.run(content, message_history=ctx.messages)
            return result.output

    return rooting_agent



def initialize_routing_agent(BasicConfig=None):

    if BasicConfig is None:
        BasicConfig = BasicConfig()

    llm_model, langfuse, logger = BasicConfig.llm_model, BasicConfig.langfuse, BasicConfig.logger
    deep_research_agent = initialize_deep_research_agent(BasicConfig=BasicConfig)
    excel_agent = initialize_excel_agent(BasicConfig=BasicConfig)
    rooting_agent = generate_routing_agent(llm_model, research_agent=deep_research_agent, excel_agent=excel_agent, langfuse=langfuse, logger=logger)
    return rooting_agent


if __name__ == "__main__":
    try:
        BasicConfig = BasicConfig()
        rooting_agent = initialize_routing_agent(BasicConfig=BasicConfig)
        logger = BasicConfig.logger
        user_request = input("Enter your question for the rooting agent: ")
        result = asyncio.run(rooting_agent.run(user_request))
        print(f"Agent Reply: {result.output}")
        print(f"/n Full Context: \n {result.all_messages}")

    except Exception as e:
        logger.error(f"Startup Failed: {e}")
        exit(1) 

    