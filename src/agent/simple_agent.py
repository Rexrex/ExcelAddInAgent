import os
import dotenv

from langfuse import get_client, observe
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

load_dotenv()  # Load environment variables from .env file

langfuse = get_client()  # Initialize Langfuse client

OPEN_ROUTER_API_KEY=os.getenv('OPEN_ROUTER_KEY')
assert OPEN_ROUTER_API_KEY is not None, "OPEN_ROUTER_KEY environment variable is not set"

DEFAUT_MODEL = os.getenv('DEFAULT_MODEL', 'deepseek/deepseek-chat-v3.1:free')


model = OpenAIChatModel(
    DEFAUT_MODEL,
    provider=OpenRouterProvider(api_key=OPEN_ROUTER_API_KEY),
)

Agent.instrument_all()
agent = Agent(model, instructions="Be Concise. Answer the question as best as you can.", instrument=True)


async def run_agent(input):
    result = await agent.run(input)  
    print(result.output)
    return result.output

@observe()
async def llm_chat(input):
    print(f"llm_chat input: {input}")
    output = await run_agent(input)
 
    langfuse.update_current_trace(
        input=input,
        output=output,
        user_id="user_123",
        session_id="session_abc",
        tags=["agent", "my-trace"],
        metadata={"email": "user@langfuse.com"},
        version="1.0.0"
    )
 
    return output

if __name__ == "__main__":
    user_request = input("Enter your question: ")
    llm_chat(user_request)