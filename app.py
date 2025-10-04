from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import dotenv
from src.agent.root_agent import initialize_agent

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


class ChatRequest(BaseModel):
    message: str
    user_id: str | None = None

root_agent = initialize_agent()

@app.post("/chat")
async def chat(body: ChatRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        return {"error": "Unauthorized"}, 401
    reply = await root_agent.run(body.message)
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
