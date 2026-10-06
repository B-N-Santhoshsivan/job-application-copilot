"""
Interview Preparation Agent:
Generates comprehensive interview prep conforming to Section 10 of course rubric:
- At least 10 Technical questions
- At least 5 Resume-based questions
- At least 5 Behavioral questions (with STAR blueprints)
- At least 5 Company-specific questions
For every question provides tested concept, recommended approach, and cited resume evidence.
Persists guide via MCP write_file tool.
"""

import re
from typing import Dict, Any
from graph.state import JobCopilotState
from agents.llm_factory import get_llm
from tools.mcp_client_tools import write_file_tool
from rag.pipeline import rag_pipeline


def interview_prep_node(state: JobCopilotState) -> Dict[str, Any]:
    candidate_name = state.get("candidate_name", "Candidate")
    company = state.get("target_company") or state.get("company_name", "Target Company")
    role = state.get("target_role", "Target Position")
    company_intel = state.get("company_research", "")

    # Retrieve candidate projects and skills from RAG
    project_citations = rag_pipeline.get_context_with_citations(
        query="projects dashboards machine learning SQL models database metrics",
        top_k=4,
        source_filter="Resume"
    )

    llm = get_llm(temperature=0.3)
    prompt = f"""You are the Interview Preparation Coach for Job Application Copilot.
Generate a rigorous, customized interview coaching manual for the candidate.

CANDIDATE: {candidate_name}
TARGET ROLE: {role}
TARGET COMPANY: {company}

VERIFIED RESUME EVIDENCE:
{project_citations}

COMPANY RESEARCH CONTEXT:
{company_intel[:400] if company_intel else f"{company} culture"}

MANDATORY GENERATION REQUIREMENTS:
1. Technical Questions: Provide AT LEAST 10 realistic questions for this role (SQL, algorithms, statistics, system design).
2. Resume-Based Questions: Provide AT LEAST 5 questions probing the candidate's actual projects/experience.
3. Behavioral Questions: Provide AT LEAST 5 questions using the STAR framework (Situation, Task, Action, Result).
4. Company-Specific Questions: Provide AT LEAST 5 questions tailored to {company}'s products, culture, and business model.

FOR EVERY SINGLE QUESTION, INCLUDE:
- Question
- What the Interviewer is Testing
- Suggested Answer Approach
- Relevant Resume Evidence (Cite candidate's actual projects; DO NOT invent fake experiences)
"""

    response = llm.invoke(prompt)
    prep_sheet_text = response.content if hasattr(response, "content") else str(response)

    # Save via MCP write_file tool
    safe_candidate = re.sub(r"[^\w\-]", "_", candidate_name).strip("_")
    safe_comp = re.sub(r"[^\w\-]", "_", company).strip("_")
    filename = f"{safe_candidate}_{safe_comp}_interview_prep.txt"

    write_file_tool.invoke({
        "filename": filename,
        "content": prep_sheet_text
    })

    output_files = list(state.get("output_files", []))
    if filename not in output_files:
        output_files.append(filename)

    return {
        "interview_tips": prep_sheet_text,
        "interview_sheet": prep_sheet_text,
        "output_files": output_files,
        "active_agent": "InterviewPrepAgent"
    }


# Backwards compatibility alias
interview_prep_agent_node = interview_prep_node

__all__ = ["interview_prep_node", "interview_prep_agent_node"]
