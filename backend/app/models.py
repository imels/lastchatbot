from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str   

class UserLogin(BaseModel):
    email: EmailStr
    password: str   

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SessionCreate(BaseModel):
    title: str

class MessageIn(BaseModel):
    session_id: str
    content: str

class FAQ(BaseModel):
    id: Optional[str] = None
    question: str
    answer: str
    tags: Optional[List[str]] = []
