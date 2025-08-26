import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import Binary

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB", "pdf_rag_chatbot")

client = AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]

# Koleksiyonlar
users_col = db["users"]
sessions_col = db["sessions"]
messages_col = db["messages"]
faqs_col = db["faqs"]
chunks_col = db["chunks"]
pdfs_col = db["pdfs"]  

# Dokümanı JSON uyumlu hale getirme
def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc
