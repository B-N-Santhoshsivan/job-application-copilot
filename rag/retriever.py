"""
Retriever for RAG Pipeline with Citation Provenance.
Queries the vector store and formats retrieved evidence with strict attribution.
"""

from typing import List, Optional, Dict, Any
from rag.ingest import DocumentChunk, chunk_document_by_section, load_pdf
from rag.vectorstore import VectorStore


class RAGRetriever:
    """
    RAG Retriever coordinating ingestion, embedding storage, and citation formatting.
    """

    def __init__(self):
        self.vector_store = VectorStore()
        self.raw_resume_text = ""
        self.raw_jd_text = ""

    def clear(self):
        self.vector_store.clear()
        self.raw_resume_text = ""
        self.raw_jd_text = ""

    def ingest(self, resume_text: str, job_description: str):
        """
        Ingest candidate resume and target job description into the vector store.
        """
        self.clear()
        self.raw_resume_text = resume_text or ""
        self.raw_jd_text = job_description or ""

        resume_chunks = chunk_document_by_section(self.raw_resume_text, source="Resume")
        jd_chunks = chunk_document_by_section(self.raw_jd_text, source="Job Description")

        self.vector_store.add_chunks(resume_chunks)
        self.vector_store.add_chunks(jd_chunks)

    def retrieve_chunks(
        self,
        query: str,
        top_k: int = 4,
        source_filter: Optional[str] = None
    ) -> List[DocumentChunk]:
        results = self.vector_store.similarity_search(query, top_k=top_k, source_filter=source_filter)
        return [chunk for chunk, _ in results]

    def get_context_with_citations(
        self,
        query: str,
        top_k: int = 4,
        source_filter: Optional[str] = None
    ) -> str:
        """
        Returns evidence chunks prefixed with explicit citation tags.
        """
        chunks = self.retrieve_chunks(query, top_k=top_k, source_filter=source_filter)
        if not chunks:
            return f"No citations found for '{query}' in {source_filter or 'documents'}."

        formatted = []
        for c in chunks:
            formatted.append(f"--- Citation: {c.citation_tag} ---\n{c.content}\n")
        return "\n".join(formatted)

    def get_all_citations(self) -> List[Dict[str, str]]:
        """
        Returns metadata for all chunks in the store for audit and reporting.
        """
        return [c.to_dict() for c in self.vector_store.chunks]


# Global singleton instance
rag_retriever = RAGRetriever()
