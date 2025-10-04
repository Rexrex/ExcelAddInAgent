import os
import dotenv

from langfuse import get_client
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

langfuse = get_client()  # Initialize Langfuse client

OPEN_ROUTER_API_KEY=os.getenv('OPEN_ROUTER_KEY')
assert OPEN_ROUTER_API_KEY is not None, "OPEN_ROUTER_KEY environment variable is not set"

MODEL = os.getenv('DEFAULT_MODEL', 'deepseek/deepseek-chat-v3.1:free')