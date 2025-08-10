from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str

class UserOut(BaseModel):
    id: int
    username: str

class UserCreate(BaseModel):
    username: str 
    password: str