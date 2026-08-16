from app.config import settings
from typing import List
import asyncio

_model = None

def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.embedding_model)
    return _model

def _embed_sync(texts: List[str]) -> List[List[float]]:
    model = _get_model()
    embeddings = model.encode(texts)
    return embeddings.tolist()

async def embed_texts(texts: List[str]) -> List[List[float]]:
    return await asyncio.to_thread(_embed_sync, texts)
