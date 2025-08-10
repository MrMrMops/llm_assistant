# tests/test_chat.py
import pytest

@pytest.mark.asyncio
async def test_send_message_to_llm(client):
    # логин и получение токена
    # response = await client.post("/login", data={
    #     "username": "testuser",
    #     "password": "testpass"
    # })
    # token = response.json()["access_token"]

    # headers = {"Authorization": f"Bearer {token}"}

    # отправка сообщения
    response = await client.post("/chat/", json={
        "prompt": "Hello, LLM!"
    }, )
    
    # assert response.status_code == 200
    data = response.json()
    print(data)
    assert "response" in data
