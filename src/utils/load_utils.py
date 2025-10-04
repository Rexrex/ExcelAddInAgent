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

OPEN_ROUTER_API_KEY, DEFAULT_MODEL = None, None

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

    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'deepseek/deepseek-chat-v3.1:free')
    assert DEFAULT_MODEL is not None, "DEFAULT_MODEL environment variable is not set"

    logger.info("Environment variables loaded successfully")
    return OPEN_ROUTER_API_KEY, DEFAULT_MODEL

# Load Langfuse
def initialize_langfuse():
    try:
        langfuse = get_client()
        logger.info("Langfuse client initialized successfully")
        return langfuse
    except Exception as e:
        logger.exception("Failed to initialize Langfuse client")
        raise e
    

def load_llm_model(OPEN_ROUTER_API_KEY, DEFAULT_MODEL):
    model = OpenAIChatModel(DEFAULT_MODEL,
        provider=OpenRouterProvider(api_key=OPEN_ROUTER_API_KEY),
        )
    return model


def load_all():
    OPEN_ROUTER_API_KEY, DEFAULT_MODEL = load_environment()
    langfuse =  initialize_langfuse()
    llm_model= load_llm_model(OPEN_ROUTER_API_KEY, DEFAULT_MODEL)
    logger.info("Setup complete")
    return llm_model, langfuse, logger

if __name__ == "__main__":
    try:
       load_all()
    except Exception as e:
        logger.error(f"Startup Failed: {e}")
        exit(1) 

    