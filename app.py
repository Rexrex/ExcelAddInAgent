import os
import dotenv

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.agent.router_agent import initialize_routing_agent
from pydantic_ai.messages import ModelMessage 
from src.utils.load_utils import BasicConfig
from typing import Dict, List

dotenv.load_dotenv()

API_KEY = os.getenv("API_KEY", "default_api_key")
assert API_KEY != "default_api_key", "Please set a secure API key in the .env file."

app = FastAPI()

origins = [
    "https://localhost:3000",
    "https://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Map from user_id → list of ModelMessage
conversation_histories: Dict[str, List[ModelMessage]] = {}

class ChatRequest(BaseModel):
    message: str
    user_id: str | None = None

BasicConfig = BasicConfig()
router_agent = initialize_routing_agent(BasicConfig)

@app.post("/chat")
async def chat(body: ChatRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        return {"error": "Unauthorized"}, 401
    
    user_id = 0
    user_msg = body.message

    # Load existing history or initialize
    history = conversation_histories.get(user_id, [])

    reply = await router_agent.run(user_msg, message_history=history)

    # Append the new messages into history
    new_msgs = reply.new_messages()
    if new_msgs:
        updated_history = history + new_msgs
        conversation_histories[user_id] = updated_history

    print(f"Reply:{reply.output}")
    print(f"UserID: {body.user_id}, Message: {body.message}, Reply: {reply}")
    return {"reply": reply.output}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
