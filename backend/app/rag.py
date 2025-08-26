import os
os.environ['CURL_CA_BUNDLE'] = ""
os.environ['SSL_CERT_FILE'] = ""

import os, io, numpy as np, faiss
from typing import List
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

FAISS_DIR = os.getenv("FAISS_DIR", "./faiss_indexes")
EMBED_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
_model: SentenceTransformer | None = None
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K = int(os.getenv("TOP_K", "6"))

os.makedirs(FAISS_DIR, exist_ok=True)

# -----------------------------
# Helper: Split text into chunks
# -----------------------------
def _split_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    chunks, start, n = [], 0, len(text)
    while start < n:
        end = min(n, start + size)
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        if end >= n: 
            break
        start = max(0, end - overlap)
    return chunks

# -----------------------------
# Initialize embedding model
# -----------------------------
def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL_NAME)
    return _model

# -----------------------------
# Embed texts locally
# -----------------------------
def embed_texts(texts: List[str]) -> np.ndarray:
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.astype("float32")

# -----------------------------
# PDF -> Chunks
# -----------------------------
def pdf_to_chunks(file_bytes: bytes) -> List[str]:
    pdf = PdfReader(io.BytesIO(file_bytes))
    text = "\n\n".join((page.extract_text() or "") for page in pdf.pages)
    return _split_text(text)

# -----------------------------
# Build FAISS index
# -----------------------------
def build_faiss_for_session(session_id: str, chunks: List[str]) -> str:
    embs = embed_texts(chunks)
    dim = embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embs)
    index_path = os.path.join(FAISS_DIR, f"{session_id}.faiss")
    faiss.write_index(index, index_path)
    return index_path

# -----------------------------
# Retrieve top-k chunks
# -----------------------------
def retrieve(session_id: str, query: str, top_k: int = TOP_K):
    index_path = os.path.join(FAISS_DIR, f"{session_id}.faiss")
    if not os.path.exists(index_path):
        return []
    index = faiss.read_index(index_path)
    q = embed_texts([query])
    scores, idxs = index.search(q, top_k)
    return idxs[0].tolist()
