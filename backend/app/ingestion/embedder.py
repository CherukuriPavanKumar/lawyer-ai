from app.config import settings
from typing import List
import asyncio

_model = None

def _get_model():
    global _model
    if _model is None:
        from fastembed import TextEmbedding
        _model = TextEmbedding(f"sentence-transformers/{settings.embedding_model}")
    return _model

def _embed_sync(texts: List[str]) -> List[List[float]]:
    model = _get_model()
    # fastembed returns a generator of numpy arrays, we want a list of lists
    embeddings = list(model.embed(texts))
    return [emb.tolist() for emb in embeddings]

async def embed_texts(texts: List[str]) -> List[List[float]]:
    return await asyncio.to_thread(_embed_sync, texts)
