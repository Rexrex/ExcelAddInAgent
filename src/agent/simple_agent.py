import os
import dotenv
import logging
import asyncio

from langfuse import get_client, observe
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

load_dotenv()  # Load environment variables from .env file

langfuse = get_client()  # Initialize Langfuse client

OPEN_ROUTER_API_KEY, DEFAUT_MODEL = None, None

Agent.instrument_all()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up the Enviroment
def load_environment():
    ## Load environment variables from .env file
    load_dotenv()

    OPEN_ROUTER_API_KEY=os.getenv('OPEN_ROUTER_KEY')
    if not OPEN_ROUTER_API_KEY:
        logger.error("OPEN_ROUTER_KEY environment variable is not set")
        raise ValueError("OPEN_ROUTER_KEY environment variable is not set")

    DEFAUT_MODEL = os.getenv('DEFAULT_MODEL', 'deepseek/deepseek-chat-v3.1:free')
    assert DEFAUT_MODEL is not None, "DEFAULT_MODEL environment variable is not set"

    logger.info("Environment variables loaded successfully")
    return OPEN_ROUTER_API_KEY, DEFAUT_MODEL

# Load Langfuse
def initialize_langfuse():
    try:
        langfuse = get_client()
        logger.info("Langfuse client initialized successfully")
        return langfuse
    except Exception as e:
        logger.exception("Failed to initialize Langfuse client")
        raise e

## Initalize the Agent
class BaseAgent():
    model = None,
    agent = None
    
    def __init__(self, OPEN_ROUTER_API_KEY, DEFAULT_MODEL):

        self.model = OpenAIChatModel(
        DEFAULT_MODEL,
        provider=OpenRouterProvider(api_key=OPEN_ROUTER_API_KEY),
        )

        self.agent = Agent(self.model, instructions="Be Concise. Answer the question as best as you can.", instrument=True)
        logger.info("Agent Setup successful")

    @observe()
    async def run(self, input):
        print(f"llm_chat input: {input}")
        result = await self.agent.run(input)  
        output = result.output
    
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
    try:
        OPEN_ROUTER_API_KEY, DEFAUT_MODEL = load_environment()
        langfuse =  initialize_langfuse()
        logger.info("Setup complete. You can now use the llm_chat function.")

        simple_agent = BaseAgent(OPEN_ROUTER_API_KEY=OPEN_ROUTER_API_KEY, DEFAULT_MODEL=DEFAUT_MODEL)
        user_request = input("Enter your question: ")
        result = asyncio.run(simple_agent.run(user_request))
        print(f"Agent Reply: {result}")

    except Exception as e:
        logger.error(f"Startup Failed: {e}")
        exit(1) 

    