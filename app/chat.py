import asyncio
import select
import time
import uuid
from app.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import async_session
from app.schemas import ChatRequest, ChatResponse
from app.models import User, Message
import httpx
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()

# OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
# OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_API_URL = "http://ollama:11434/api/generate"



@router.post("/")
async def get_ai_response(prompt: ChatRequest, user = Depends(get_current_user)):
    # Форматируем промпт по спецификации Llama 3
    formatted_prompt = (
        "<|begin_of_text|>"
        "<|start_header_id|>system<|end_header_id|>"
        "You are helpful assistant. Answer concisely.<|eot_id|>"
        "<|start_header_id|>user<|end_header_id|>"
        f"{prompt.prompt}<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>"
    )
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "http://ollama:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": formatted_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,  # Для креативности
                        "num_ctx": 4096,
                        "repeat_penalty": 1.2,  # Штраф за повторения
                        "seed": int(time.time())  # Уникальное зерно
                    }
                }
            )

            


            result = response.json()

            async with async_session() as db:
                message = Message(user_id=user.id, prompt=prompt.prompt, response=result["response"])
                db.add(message)
                await db.commit()

            return result
            
    except Exception as e: 
        raise HTTPException(500, f"Ollama error: {str(e)}")

