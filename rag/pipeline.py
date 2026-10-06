"""
RAG Pipeline Interface for Job Application Copilot.
Wraps ingest, vector store, and retriever for backwards compatibility and clean imports.
"""

from rag.ingest import DocumentChunk, chunk_document_by_section, load_pdf
from rag.vectorstore import VectorStore
from rag.retriever import RAGRetriever, rag_retriever


class SessionRAGPipeline:
    def __init__(self):
        self.retriever = rag_retriever

    def clear(self):
        self.retriever.clear()

    def ingest_documents(self, resume_text: str, job_description: str):
        self.retriever.ingest(resume_text, job_description)

    def retrieve(self, query: str, top_k: int = 4, source_filter=None):
        return self.retriever.retrieve_chunks(query, top_k=top_k, source_filter=source_filter)

    def get_context_with_citations(self, query: str, top_k: int = 4, source_filter=None) -> str:
        return self.retriever.get_context_with_citations(query, top_k=top_k, source_filter=source_filter)

    @property
    def chunks(self):
        return self.retriever.vector_store.chunks


rag_pipeline = SessionRAGPipeline()

__all__ = ["rag_pipeline", "rag_retriever", "SessionRAGPipeline", "DocumentChunk", "load_pdf", "VectorStore", "RAGRetriever"]
