# app/auth.py
from fastapi import APIRouter, HTTPException, Header
from .models import UserCreate, UserLogin, TokenOut
from .utils import hash_password, verify_password, create_access_token, decode_token
from .db import users_col
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
async def register(user: UserCreate):
    existing = await users_col.find_one({"email": user.email})
    if existing:
        raise HTTPException(409, "Email already registered")
    doc = {
        "email": user.email,
        "password": hash_password(user.password),
        "name": user.name,
        "created_at": datetime.utcnow(),
    }
    res = await users_col.insert_one(doc)
    token = create_access_token(str(res.inserted_id))
    return {"access_token": token}


@router.post("/login", response_model=TokenOut)
async def login(user: UserLogin):  # ✅ sadece email + password
    found = await users_col.find_one({"email": user.email})
    if not found or not verify_password(user.password, found["password"]):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token(str(found["_id"]))
    return {"access_token": token}


async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing token")
    token = authorization.split(" ")[1]
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(401, "Invalid token")
    user = await users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(401, "User not found")
    return user
