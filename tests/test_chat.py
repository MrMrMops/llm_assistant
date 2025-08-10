# tests/test_chat.py
import random
import uuid
import pytest
from app.db import get_async_session

@pytest.mark.asyncio
async def test_send_message_to_llm(client):
    # логин и получение токена
    username = 'test_user_' + str(random.randint(1,10000))

    response = await client.post("/auth/register", json = {
        "username": username,
        "password": "testpass"
    })

    assert response.status_code == 200

    response = await client.post("/auth/login", data={
        "username": username,
        "password": "testpass"
    })
    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # отправка сообщения
    response = await client.post("/chat/", json={
        "prompt": "Hello, LLM!"
    }, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    print(data)
    assert "response" in data
