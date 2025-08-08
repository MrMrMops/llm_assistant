import asyncio
import time
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
# OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_API_URL = "http://ollama:11434/api/generate"

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # Здесь должен быть код для верификации JWT и получение пользователя
    # Для упрощения пока заглушка — реализуем позже
    # Например, декодируем JWT, ищем в БД
    raise HTTPException(status_code=501, detail="Not implemented")

@router.post("/")
async def get_ai_response(prompt: ChatRequest):
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
                    "context": None,  # Критически важно!
                    "options": {
                        "temperature": 0.7,  # Для креативности
                        "num_ctx": 4096,
                        "repeat_penalty": 1.2,  # Штраф за повторения
                        "seed": int(time.time())  # Уникальное зерно
                    }
                }
            )
            result = response.json()
            return result
            
    except Exception as e:
        raise HTTPException(500, f"Ollama error: {str(e)}")
        
# async def chat_endpoint(chat_req: ChatRequest):
#     async with httpx.AsyncClient() as client:
#         try:
#             payload = {
#                 "model": "llama3",
#                 "prompt": chat_req.prompt
#             }
#             resp = await client.post(OLLAMA_API_URL, json=payload)
#             resp.raise_for_status()
#             data = resp.json()
#             text = data.get("completion") or data.get("text") or ""
        
#         # Добавляем повторные попытки
#             for _ in range(3):
#                 try:
#                      await client.post(OLLAMA_API_URL, json=payload)
#                      resp.raise_for_status()
#                      data = resp.json()
#                      text = data.get("completion") or data.get("text") or ""
                     
#                 except ConnectionError:
#                     await asyncio.sleep(5)  # Ждем 5 сек перед повтором
#             raise HTTPException(503, "Ollama not ready")
#         except httpx.HTTPError as e:
#             raise HTTPException(status_code=500, detail=f"Error communicating with LLM server: {str(e)}")

    # Сохраняем в БД
    # async with async_session() as db:
    #     message = Message(user_id=user.id, prompt=chat_req.prompt, response=text)
    #     db.add(message)
    #     await db.commit()

    # return ChatResponse(response=text)
