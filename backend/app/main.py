import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from dotenv import load_dotenv
from datetime import datetime
import os

from .db import sessions_col, messages_col, chunks_col, pdfs_col
from .auth import router as auth_router, get_current_user
from .faqs import router as faqs_router
from .models import MessageIn
from .rag import pdf_to_chunks, build_faiss_for_session, retrieve
from .llm import chat_completion

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY bulunamadı! Lütfen .env dosyasını kontrol et.")

# -----------------------------
# FastAPI & CORS
# -----------------------------
app = FastAPI(title="PDF RAG Chatbot")

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Routers
# -----------------------------
app.include_router(auth_router)
app.include_router(faqs_router)

# -----------------------------
# Helper: ObjectId -> str
# -----------------------------
def serialize_doc(doc):
    if not doc:
        return None
    doc = dict(doc)
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    if "user_id" in doc and isinstance(doc["user_id"], ObjectId):
        doc["user_id"] = str(doc["user_id"])
    return doc

# -----------------------------
# Root endpoint
# -----------------------------
@app.get("/")
async def root():
    return {"ok": True}

# -----------------------------
# PDF Upload & Chunks
# -----------------------------
@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    file_bytes = await file.read()

    pdf_doc = {"filename": file.filename, "data": file_bytes}
    result = await pdfs_col.insert_one(pdf_doc)
    pdf_id = str(result.inserted_id)

    chunks = pdf_to_chunks(file_bytes)
    for i, chunk in enumerate(chunks):
        await chunks_col.insert_one({
            "pdf_id": pdf_id,
            "chunk_index": i,
            "text": chunk
        })

    build_faiss_for_session(pdf_id, chunks)

    return {"status": "success", "pdf_id": pdf_id, "chunks": len(chunks)}

@app.get("/pdf_chunks/{pdf_id}")
async def get_pdf_chunks(pdf_id: str):
    cursor = chunks_col.find({"pdf_id": pdf_id})
    chunk_list = []
    async for doc in cursor:
        chunk_list.append(serialize_doc(doc))
    return chunk_list

# -----------------------------
# SESSION ENDPOINTS
# -----------------------------
@app.post("/session/")
async def create_session(title: str = Form(...), user=Depends(get_current_user)):
    doc = {"title": title, "user_id": str(user["_id"]), "created_at": datetime.utcnow()}
    res = await sessions_col.insert_one(doc)
    session_id = str(res.inserted_id)

    await messages_col.insert_one({
        "session_id": session_id,
        "user_id": str(user["_id"]),
        "role": "assistant",
        "content": "Merhaba, nasıl yardımcı olabilirim?",
        "created_at": datetime.utcnow(),
    })
    
    return {"id": session_id, "title": title, "created_at": doc["created_at"]}

@app.get("/session/list")
async def list_sessions(user=Depends(get_current_user)):
    items = []
    async for d in sessions_col.find({"user_id": str(user["_id"])}).sort("created_at", -1):
        items.append({
            "id": str(d["_id"]),
            "title": d.get("title", ""),
            "created_at": d.get("created_at")
        })
    return items

@app.delete("/session/delete/{session_id}")
async def delete_session(session_id: str, user=Depends(get_current_user)):
    ses = await sessions_col.find_one({"_id": ObjectId(session_id), "user_id": str(user["_id"])})
    if not ses:
        raise HTTPException(status_code=404, detail="Session not found")

    await messages_col.delete_many({"session_id": session_id})
    await chunks_col.delete_many({"session_id": session_id})
    await sessions_col.delete_one({"_id": ObjectId(session_id)})

    return {"ok": True, "id": session_id}

# -----------------------------
# SESSION PDF UPLOAD
# -----------------------------
@app.post("/session/{session_id}/upload")
async def upload_pdf_session(session_id: str, pdf: UploadFile = File(...), user=Depends(get_current_user)):
    ses = await sessions_col.find_one({"_id": ObjectId(session_id), "user_id": str(user["_id"])})
    if not ses:
        raise HTTPException(status_code=404, detail="Session not found")

    data = await pdf.read()
    chunks = pdf_to_chunks(data)
    if not chunks:
        raise HTTPException(status_code=400, detail="No text could be extracted from PDF")

    index_path = build_faiss_for_session(session_id, chunks)

    await chunks_col.delete_many({"session_id": session_id})
    await chunks_col.insert_many([
        {"session_id": session_id, "user_id": str(user["_id"]), "chunk_index": i, "text": c}
        for i, c in enumerate(chunks)
    ])

    await sessions_col.update_one({"_id": ObjectId(session_id)}, {"$set": {"faiss_index_path": index_path}})
    return {"ok": True, "index_path": index_path, "chunks": len(chunks)}

# -----------------------------
# CHAT ENDPOINTS
# -----------------------------
@app.get("/chat/history/{session_id}")
async def chat_history(session_id: str, user=Depends(get_current_user)):
    ses = await sessions_col.find_one({"_id": ObjectId(session_id), "user_id": str(user["_id"])})
    if not ses:
        raise HTTPException(status_code=404, detail="Session not found")

    msgs = []
    async for m in messages_col.find({"session_id": session_id}).sort("created_at", 1):
        msgs.append({
            "id": str(m["_id"]),
            "role": m["role"],
            "content": m["content"],
            "created_at": m["created_at"],
        })
    return msgs

@app.post("/chat/ask")
async def chat_ask(payload: MessageIn, user=Depends(get_current_user)):
    ses = await sessions_col.find_one({"_id": ObjectId(payload.session_id), "user_id": str(user["_id"])})
    if not ses:
        raise HTTPException(status_code=404, detail="Session not found")

    # Kullanıcı mesajını kaydet
    umsg = {
        "session_id": payload.session_id,
        "user_id": str(user["_id"]),
        "role": "user",
        "content": payload.content,
        "created_at": datetime.utcnow(),
    }
    await messages_col.insert_one(umsg)

    # Geçmiş mesajlar
    history_messages = []
    async for m in messages_col.find({"session_id": payload.session_id}).sort("created_at", 1):
        history_messages.append({"role": m["role"], "content": m["content"]})

    # FAISS retrieval
    idxs = retrieve(payload.session_id, payload.content)
    ctx_texts = []
    for rank, i in enumerate(idxs, start=1):
        meta = await chunks_col.find_one({"session_id": payload.session_id, "chunk_index": i})
        if meta and meta.get("text"):
            ctx_texts.append(f"[Chunk #{rank}]\n{meta['text']}")

    context_text = "\n\n".join(ctx_texts)
    prompt_with_context = payload.content
    if context_text:
        prompt_with_context = f"PDF'den gelen bağlam:\n\n{context_text}\n\nSoru: {payload.content}\n\nTalimat: Sadece bağlamdaki bilgilere dayanarak cevapla. Cevabın kısa ve öz olsun. Eğer bağlam yoksa, 'Üzgünüm, bu konuyla ilgili bilgi bulamadım.' de."

    messages = history_messages + [{"role": "user", "content": prompt_with_context}]
    answer = chat_completion(messages)

    await messages_col.insert_one({
        "session_id": payload.session_id,
        "user_id": str(user["_id"]),
        "role": "assistant",
        "content": answer,
        "created_at": datetime.utcnow(),
    })

    return {"answer": answer, "contexts": [{"rank": r+1, "chunk_index": i} for r, i in enumerate(idxs)]}
