"""
junior2api — Junior.so → OpenAI-compatible API
Entry point: uvicorn main:app
"""

import asyncio
import json
import time
import uuid
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from auth import SessionManager
from config import settings
from models import ChatCompletionRequest, ChatCompletionResponse, Choice, Message, Usage

app = FastAPI(title="junior2api", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

session_manager = SessionManager()


@app.on_event("startup")
async def startup():
    await session_manager.init()


@app.get("/")
async def root():
    return {"status": "ok", "service": "junior2api"}


@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {"id": "junior", "object": "model", "created": 0, "owned_by": "junior.so"}
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest, req: Request):
    user_message = ""
    for msg in reversed(request.messages):
        if msg.role == "user":
            user_message = msg.content
            break

    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found")

    if request.stream:
        return StreamingResponse(
            stream_response(user_message),
            media_type="text/event-stream",
        )

    reply = await session_manager.send_message(user_message)
    response = ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
        created=int(time.time()),
        model=request.model or "junior",
        choices=[
            Choice(
                index=0,
                message=Message(role="assistant", content=reply),
                finish_reason="stop",
            )
        ],
        usage=Usage(
            prompt_tokens=len(user_message.split()),
            completion_tokens=len(reply.split()),
            total_tokens=len(user_message.split()) + len(reply.split()),
        ),
    )
    return response


async def stream_response(user_message: str) -> AsyncGenerator[str, None]:
    reply = await session_manager.send_message(user_message)
    chunk_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"

    words = reply.split(" ")
    for i, word in enumerate(words):
        chunk = {
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "junior",
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": word + (" " if i < len(words) - 1 else "")},
                    "finish_reason": None,
                }
            ],
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        await asyncio.sleep(0.02)

    final = {
        "id": chunk_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "junior",
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
    }
    yield f"data: {json.dumps(final)}\n\n"
    yield "data: [DONE]\n\n"
