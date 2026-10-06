"""
Document Ingestion & Chunking for RAG Pipeline.
Supports PDF resumes, text documents, and section-aware semantic chunking.
"""

import os
import re
from pathlib import Path
from typing import List, Optional


class DocumentChunk:
    def __init__(self, content: str, source: str, section: str, chunk_id: str):
        self.content = content.strip()
        self.source = source.strip()
        self.section = section.strip()
        self.chunk_id = chunk_id

    @property
    def citation_tag(self) -> str:
        return f"[{self.source}: Section '{self.section}']"

    def to_dict(self):
        return {
            "chunk_id": self.chunk_id,
            "source": self.source,
            "section": self.section,
            "citation": self.citation_tag,
            "content": self.content
        }


def load_pdf(file_path_or_bytes) -> str:
    """
    Extracts text from a PDF file or bytes using pypdf if available,
    with a graceful regex/string fallback for pure PDF streams.
    """
    # 1. Try pypdf
    try:
        from pypdf import PdfReader
        if isinstance(file_path_or_bytes, (str, Path)):
            reader = PdfReader(str(file_path_or_bytes))
        else:
            import io
            reader = PdfReader(io.BytesIO(file_path_or_bytes))
        
        extracted = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted.append(text)
        if extracted:
            return "\n\n".join(extracted)
    except Exception:
        pass

    # 2. Try PyPDFLoader from langchain_community
    try:
        from langchain_community.document_loaders import PyPDFLoader
        if isinstance(file_path_or_bytes, (str, Path)):
            loader = PyPDFLoader(str(file_path_or_bytes))
            docs = loader.load()
            return "\n\n".join(d.page_content for d in docs)
    except Exception:
        pass

    # 3. Fallback: Parse standard PDF text operators (BT ... ET)
    try:
        if isinstance(file_path_or_bytes, (str, Path)):
            with open(file_path_or_bytes, "rb") as f:
                raw_bytes = f.read()
        else:
            raw_bytes = file_path_or_bytes

        # Extract text in parentheses between BT and ET
        text_matches = re.findall(rb"\((.*?)\)\s*['\"]?", raw_bytes)
        if text_matches:
            decoded = [m.decode("latin1", "ignore").replace(r"\(", "(").replace(r"\)", ")") for m in text_matches]
            return "\n".join(decoded)
    except Exception:
        pass

    return ""


def chunk_document_by_section(text: str, source: str) -> List[DocumentChunk]:
    """
    Splits document into section-aware chunks based on heading keywords.
    Ensures every chunk retains semantic section context for citation provenance.
    """
    if not text or not text.strip():
        return []

    lines = [line.strip() for line in text.splitlines()]
    current_section = "General Overview"
    current_buffer: List[str] = []
    chunks: List[DocumentChunk] = []
    chunk_idx = 1

    common_headers = [
        "OBJECTIVE", "SUMMARY", "PROFESSIONAL SUMMARY", "CAREER OBJECTIVE",
        "EDUCATION", "ACADEMIC BACKGROUND", "QUALIFICATIONS",
        "SKILLS", "TECHNICAL SKILLS", "CORE COMPETENCIES", "PROGRAMMING LANGUAGES",
        "PROJECTS", "ACADEMIC PROJECTS", "KEY PROJECTS", "PERSONAL PROJECTS",
        "EXPERIENCE", "INTERNSHIP EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT HISTORY",
        "CERTIFICATIONS", "ACHIEVEMENTS", "HONORS", "PUBLICATIONS",
        "ABOUT", "ABOUT COMPANY", "OVERVIEW", "JOB OVERVIEW", "ROLE SUMMARY",
        "RESPONSIBILITIES", "KEY RESPONSIBILITIES", "DUTIES",
        "MINIMUM QUALIFICATIONS", "PREFERRED QUALIFICATIONS", "REQUIREMENTS", "BENEFITS"
    ]

    for line in lines:
        if not line:
            continue

        clean_line = line.strip("#-* :").upper()
        is_header = False

        for h in common_headers:
            if clean_line == h or clean_line.startswith(h + ":") or clean_line.endswith(h):
                is_header = True
                break

        if is_header and current_buffer:
            content = "\n".join(current_buffer).strip()
            if content:
                chunk_id = f"{source.lower().replace(' ', '_')}_{chunk_idx}"
                chunks.append(DocumentChunk(content, source, current_section, chunk_id))
                chunk_idx += 1
            current_section = line.strip("#-* :")
            current_buffer = []
        else:
            current_buffer.append(line)

    if current_buffer:
        content = "\n".join(current_buffer).strip()
        if content:
            chunk_id = f"{source.lower().replace(' ', '_')}_{chunk_idx}"
            chunks.append(DocumentChunk(content, source, current_section, chunk_id))

    return chunks
