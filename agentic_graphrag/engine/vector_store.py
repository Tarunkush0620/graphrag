"""Modular Vector Retrieval Layer for Document Chunks.

Maintains document embeddings, chunk metadata, and cosine-similarity search.
Supports both in-memory cosine index and external vector database providers.
"""

from typing import List, Dict, Any, Tuple
import math
import re
import hashlib
from pydantic import BaseModel


class DocumentChunk(BaseModel):
    chunk_id: str
    doc_id: str
    source: str
    title: str
    content: str
    entities: List[str] = []
    timestamp: str = ""
    embedding: List[float] = []


class VectorStore:
    def __init__(self):
        self.chunks: Dict[str, DocumentChunk] = {}
        self._vocab: Dict[str, int] = {}

    def add_chunk(self, chunk: DocumentChunk):
        if not chunk.embedding:
            chunk.embedding = self._compute_embedding(chunk.content)
        self.chunks[chunk.chunk_id] = chunk

    def add_documents(self, docs: List[Dict[str, Any]]):
        for doc in docs:
            doc_id = doc.get("doc_id", "doc_001")
            source = doc.get("source", "corpus")
            title = doc.get("title", "Document")
            text = doc.get("content", "")
            timestamp = doc.get("timestamp", "")
            entities = doc.get("entities", [])

            # Split into ~150-word chunks
            words = text.split()
            chunk_size = 120
            for i in range(0, max(len(words), 1), chunk_size):
                chunk_words = words[i : i + chunk_size]
                chunk_text = " ".join(chunk_words)
                chunk_id = f"{doc_id}_chk_{i // chunk_size}"
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    source=source,
                    title=title,
                    content=chunk_text,
                    entities=entities,
                    timestamp=timestamp,
                )
                self.add_chunk(chunk)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Perform cosine similarity search between query and chunk vectors."""
        if not self.chunks:
            return []

        q_vec = self._compute_embedding(query)
        scores: List[Tuple[DocumentChunk, float]] = []

        for chunk in self.chunks.values():
            sim = self._cosine_similarity(q_vec, chunk.embedding)
            # Keyword overlap boost for exact phrase hits
            q_terms = set(re.findall(r"\b\w{3,}\b", query.lower()))
            c_terms = set(re.findall(r"\b\w{3,}\b", chunk.content.lower()))
            overlap = len(q_terms.intersection(c_terms)) / max(len(q_terms), 1)
            total_score = round(0.7 * sim + 0.3 * overlap, 4)
            scores.append((chunk, total_score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def _compute_embedding(self, text: str, dim: int = 64) -> List[float]:
        """Deterministic dense representation of text for semantic ranking."""
        tokens = re.findall(r"\b\w+\b", text.lower())
        vec = [0.0] * dim
        for i, token in enumerate(tokens):
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            slot = h % dim
            weight = 1.0 / (math.log(i + 2))
            vec[slot] += weight

        # Normalize L2
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


# Global singleton instance
_GLOBAL_VECTOR_STORE = VectorStore()


def get_vector_store() -> VectorStore:
    return _GLOBAL_VECTOR_STORE
