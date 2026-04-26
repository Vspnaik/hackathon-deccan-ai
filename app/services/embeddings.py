"""
Embedding service using local Sentence Transformers.
Wraps model loading and encoding for reuse across modules.
"""
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

_model = None


def get_model() -> SentenceTransformer:
    """Lazy-load the embedding model singleton."""
    global _model
    if _model is None:
        print(f"[Embeddings] Loading model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
        print(f"[Embeddings] Model loaded. Dimension: {_model.get_sentence_embedding_dimension()}")
    return _model


def encode_text(text: str) -> list:
    """Encode a single text string to an embedding vector."""
    model = get_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def encode_texts(texts: list) -> list:
    """Encode a batch of text strings to embedding vectors."""
    model = get_model()
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True, batch_size=32)
    return [e.tolist() for e in embeddings]
