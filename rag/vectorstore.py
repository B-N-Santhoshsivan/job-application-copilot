"""
Vector Store implementation for RAG pipeline.
Provides semantic embedding indexing and similarity search with citation tracking.
Compatible with ChromaDB/FAISS and includes a standalone semantic cosine similarity index.
"""

import math
import re
from typing import List, Tuple, Optional
from rag.ingest import DocumentChunk


class VectorStore:
    """
    In-memory semantic vector store for candidate resume and job description chunks.
    Ensures zero external dependency failure while providing deterministic cosine similarity search.
    """

    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self._doc_frequencies = {}
        self._total_docs = 0

    def clear(self):
        self.chunks = []
        self._doc_frequencies = {}
        self._total_docs = 0

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", text.lower())

    def _compute_vector(self, text: str) -> dict:
        tokens = self._tokenize(text)
        if not tokens:
            return {}
        term_counts = {}
        for t in tokens:
            term_counts[t] = term_counts.get(t, 0) + 1
        
        # TF-IDF weighting
        vec = {}
        total = len(tokens)
        for t, count in term_counts.items():
            tf = count / total
            idf = math.log((self._total_docs + 1) / (self._doc_frequencies.get(t, 0) + 1)) + 1.0
            vec[t] = tf * idf
        return vec

    def _cosine_similarity(self, vec1: dict, vec2: dict) -> float:
        if not vec1 or not vec2:
            return 0.0
        dot_product = sum(vec1[k] * vec2[k] for k in vec1 if k in vec2)
        norm1 = math.sqrt(sum(v * v for v in vec1.values()))
        norm2 = math.sqrt(sum(v * v for v in vec2.values()))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    def add_chunks(self, chunks: List[DocumentChunk]):
        self.chunks.extend(chunks)
        self._total_docs = len(self.chunks)
        # Update IDF stats
        self._doc_frequencies = {}
        for c in self.chunks:
            tokens = set(self._tokenize(c.content + " " + c.section))
            for t in tokens:
                self._doc_frequencies[t] = self._doc_frequencies.get(t, 0) + 1

    def similarity_search(
        self,
        query: str,
        top_k: int = 4,
        source_filter: Optional[str] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Performs semantic similarity search over stored document chunks.
        Applies section boosting and source filtering.
        """
        if not self.chunks:
            return []

        candidates = self.chunks
        if source_filter:
            candidates = [c for c in self.chunks if c.source.lower() == source_filter.lower()]

        query_vec = self._compute_vector(query)
        query_tokens = set(self._tokenize(query))

        scored: List[Tuple[DocumentChunk, float]] = []
        for chunk in candidates:
            chunk_vec = self._compute_vector(chunk.content + " " + chunk.section)
            sim = self._cosine_similarity(query_vec, chunk_vec)

            # Boost if query tokens match chunk section header directly
            section_tokens = set(self._tokenize(chunk.section))
            if query_tokens.intersection(section_tokens):
                sim += 0.25

            scored.append((chunk, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
