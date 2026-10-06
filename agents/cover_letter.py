"""
Cover Letter Agent:
Generates a professional, highly tailored cover letter (approx. 300–450 words)
grounded strictly in candidate resume facts, job description, and verified company research.
NEVER invents projects, experience, degrees, or metrics.
Persists document using the custom MCP write_file tool to:
outputs/<candidate_name>_<company>_cover_letter.txt
and logs application via MCP save_application tool.
"""

import os
import re
from typing import Dict, Any
from graph.state import JobCopilotState
from agents.llm_factory import get_llm
from tools.mcp_client_tools import write_file_tool, save_application_tool
from rag.pipeline import rag_pipeline


def cover_letter_node(state: JobCopilotState) -> Dict[str, Any]:
    candidate_name = state.get("candidate_name", "Candidate")
    company = state.get("target_company") or state.get("company_name", "Target Company")
    role = state.get("target_role", "Target Position")
    company_intel = state.get("company_research", "")
    match_score = state.get("match_score", 85)

    # Retrieve factual resume projects and experience via RAG
    resume_facts = rag_pipeline.get_context_with_citations(
        query="projects experience achievements metrics technical skills internship education",
        top_k=4,
        source_filter="Resume"
    )

    llm = get_llm(temperature=0.3)
    prompt = f"""You are the Cover Letter Agent for Job Application Copilot.
Write a tailored, professional cover letter for the candidate applying for the '{role}' role at '{company}'.

STRICT ANTI-FABRICATION GUARDRAILS:
1. Ground the letter ONLY in the factual candidate resume evidence provided below.
2. NEVER invent experiences, employers, technologies, degrees, or metrics not present in the resume.
3. If information is missing, write around it professionally rather than fabricating.
4. Word count MUST be between 300 and 450 words.
5. Tone: professional, authentic, engaging, non-generic.

CANDIDATE NAME: {candidate_name}
TARGET ROLE: {role}
TARGET COMPANY: {company}

FACTUAL RESUME EVIDENCE:
{resume_facts}

VERIFIED COMPANY RESEARCH:
{company_intel[:500] if company_intel else f"{company} is known for technical excellence and impact."}

Write the complete cover letter including formal salutation and sign-off.
"""

    response = llm.invoke(prompt)
    cover_letter_text = response.content if hasattr(response, "content") else str(response)

    # Enforce standard filename format: outputs/<candidate_name>_<company>_cover_letter.txt
    safe_candidate = re.sub(r"[^\w\-]", "_", candidate_name).strip("_")
    safe_comp = re.sub(r"[^\w\-]", "_", company).strip("_")
    filename = f"{safe_candidate}_{safe_comp}_cover_letter.txt"

    # Save via MCP write_file tool
    write_file_tool.invoke({
        "filename": filename,
        "content": cover_letter_text
    })

    # Save application via MCP save_application tool
    save_application_tool.invoke({
        "company": company,
        "role": role,
        "status": "Applied",
        "notes": f"Automated copilot submission. Match score: {match_score}/100. Saved {filename}."
    })

    output_files = list(state.get("output_files", []))
    if filename not in output_files:
        output_files.append(filename)

    return {
        "cover_letter": cover_letter_text,
        "output_files": output_files,
        "active_agent": "CoverLetterAgent"
    }


# Backwards compatibility alias
cover_letter_agent_node = cover_letter_node

__all__ = ["cover_letter_node", "cover_letter_agent_node"]
