from fastapi import APIRouter, HTTPException, Depends
from app.models import SessionCreate
from app.auth import get_current_user
from app.db import sessions_col
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/session", tags=["session"])

@router.get("/list")
async def list_sessions(user=Depends(get_current_user)):
    user_id = str(user["_id"])
    sessions = await sessions_col.find({"user_id": user_id}).to_list(100)
    # id alanını string yap
    for s in sessions:
        s["id"] = str(s["_id"])
    return sessions

@router.post("/")
async def create_session(session: SessionCreate, user=Depends(get_current_user)):
    doc = {
        "title": session.title,
        "user_id": str(user["_id"]),
        "created_at": datetime.utcnow(),
        "messages": [],
    }
    res = await sessions_col.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    return doc

__all__ = ["router"]
