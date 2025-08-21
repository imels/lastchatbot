import os, io, numpy as np, faiss, requests
from typing import List
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# .env yükle
load_dotenv()

FAISS_DIR = os.getenv("FAISS_DIR", "./faiss_indexes")
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "text-embedding-004")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K = int(os.getenv("TOP_K", "6"))

os.makedirs(FAISS_DIR, exist_ok=True)

if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY bulunamadı! Lütfen .env dosyasını kontrol et.")

def _split_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    chunks, start, n = [], 0, len(text)
    while start < n:
        end = min(n, start + size)
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        if end >= n: break
        start = max(0, end - overlap)
    return chunks

def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Google Gemini embedding API çağrısı
    Hata debug için payload ve response loglanır
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{EMBED_MODEL}:embedContent?key={GOOGLE_API_KEY}"
    vecs = []

    for t in texts:
        payload = {"model": EMBED_MODEL, "content": {"parts": [{"text": t}]}}
        print("📤 Embedding payload:", payload)  # Log payload

        try:
            r = requests.post(url, json=payload, timeout=60, verify=False)
            r.raise_for_status()
            data = r.json()
            print("📥 Embedding response keys:", list(data.keys()))  # Log yanıt anahtarları

            if "embedding" not in data or "values" not in data["embedding"]:
                print("❌ Embedding verisi yok!", data)
                raise ValueError("Embedding API yanıtı beklenmedik formatta")

            vec = data["embedding"]["values"]
            vecs.append(vec)

        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error: {e}, Response: {r.text}")
            raise

        except Exception as e:
            print(f"❌ Genel Hata: {e}")
            raise

    return np.array(vecs, dtype="float32")


def pdf_to_chunks(file_bytes: bytes) -> List[str]:
    pdf = PdfReader(io.BytesIO(file_bytes))
    text = "\n\n".join((page.extract_text() or "") for page in pdf.pages)
    return _split_text(text)

def build_faiss_for_session(session_id: str, chunks: List[str]) -> str:
    embs = embed_texts(chunks)
    faiss.normalize_L2(embs)
    dim = embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embs)
    index_path = os.path.join(FAISS_DIR, f"{session_id}.faiss")
    faiss.write_index(index, index_path)
    return index_path

def retrieve(session_id: str, query: str, top_k: int = TOP_K):
    index_path = os.path.join(FAISS_DIR, f"{session_id}.faiss")
    if not os.path.exists(index_path):
        return []
    index = faiss.read_index(index_path)
    q = embed_texts([query])
    faiss.normalize_L2(q)
    scores, idxs = index.search(q, top_k)
    return idxs[0].tolist()
