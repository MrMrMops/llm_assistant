import asyncio
from asyncio.log import logger
from fastapi import FastAPI
from app.auth import router as auth_router
from app.chat import router as chat_router

app = FastAPI(title="LLM API Assistant")

app.include_router(auth_router, prefix="/auth")
app.include_router(chat_router, prefix="/chat")

@app.on_event("startup")
async def startup():
    logger.info("Ожидание загрузки Ollama...")
    await asyncio.sleep(30)  # Дополнительная задержка