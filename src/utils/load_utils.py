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

Agent.instrument_all()

class BasicConfig:
    llm_model = None
    langfuse = None
    logger = None

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def __init__(self):
        OPEN_ROUTER_API_KEY, DEFAULT_MODEL = self.load_environment()
        self.initialize_langfuse()
        self.load_llm_model(OPEN_ROUTER_API_KEY, DEFAULT_MODEL)
        self.logger.info("Setup complete")

    # Set up the Enviroment
    def load_environment(self):
        ## Load environment variables from .env file
        load_dotenv()

        OPEN_ROUTER_API_KEY=os.getenv('OPEN_ROUTER_KEY')
        if not OPEN_ROUTER_API_KEY:
            self.logger.error("OPEN_ROUTER_KEY environment variable is not set")
            raise ValueError("OPEN_ROUTER_KEY environment variable is not set")

        CHOSEN_MODEL = os.getenv('CHOSEN_MODEL', 'DEEPSEEK')
        assert CHOSEN_MODEL in ['DEEPSEEK', 'Z-AI', 'GEMINI'], "CHOSEN_MODEL must be either 'DEEPSEEK' or 'Z-AI'"
        if CHOSEN_MODEL == 'DEEPSEEK':
             DEFAULT_MODEL = os.getenv('DEEPSEEK', 'deepseek/deepseek-chat-v3.1:free')
        elif CHOSEN_MODEL == 'Z-AI':
             DEFAULT_MODEL = os.getenv('Z-AI', 'z-ai/glm-4.5-air:free')
        elif CHOSEN_MODEL == 'GEMINI':
             DEFAULT_MODEL = os.getenv('GEMINI', 'google/gemini-2.5-flash-lite-preview-09-2025')

        assert DEFAULT_MODEL is not None, "DEFAULT_MODEL environment variable is not set"

        self.logger.info("Environment variables loaded successfully")
        return OPEN_ROUTER_API_KEY, DEFAULT_MODEL

    # Load Langfuse
    def initialize_langfuse(self):
        try:
            self.langfuse = get_client()
            self.logger.info("Langfuse client initialized successfully")
        except Exception as e:
            self.logger.exception("Failed to initialize Langfuse client")
            raise e
        

    def load_llm_model(self, OPEN_ROUTER_API_KEY, DEFAULT_MODEL):
        self.llm_model = OpenAIChatModel(DEFAULT_MODEL,
            provider=OpenRouterProvider(api_key=OPEN_ROUTER_API_KEY),
            )


if __name__ == "__main__":
    try:
        config = BasicConfig()
    except Exception as e:
        exit(1) 

    