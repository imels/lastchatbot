from fastapi import APIRouter, HTTPException, Depends
from .db import faqs_col
from .auth import get_current_user
from .models import FAQ
from bson import ObjectId

router = APIRouter(prefix="/faqs", tags=["faqs"])

@router.get("/")
async def list_faqs():
    items = []
    async for d in faqs_col.find().sort("_id", -1):
        d["id"] = str(d.pop("_id"))
        items.append(d)
    return items

@router.post("/", dependencies=[Depends(get_current_user)])
async def create_faq(item: FAQ):
    doc = {"question": item.question, "answer": item.answer, "tags": item.tags or []}
    res = await faqs_col.insert_one(doc)
    return {"id": str(res.inserted_id), **doc}

@router.delete("/{faq_id}", dependencies=[Depends(get_current_user)])
async def delete_faq(faq_id: str):
    res = await faqs_col.delete_one({"_id": ObjectId(faq_id)})
    if res.deleted_count == 0:
        raise HTTPException(404, "Not found")
    return {"ok": True}
