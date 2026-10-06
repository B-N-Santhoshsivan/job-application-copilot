"""
Resume Tools:
Extracts skills, technical competencies, and educational background from resumes.
Enforces strict anti-hallucination guardrail: extracts ONLY what is explicitly mentioned.
"""

import json
import re
from typing import Dict, List, Any

# Curated vocabulary of recognized tech skills and frameworks for deterministic extraction
KNOWN_SKILLS = [
    # Languages
    "python", "sql", "javascript", "typescript", "java", "c++", "c#", "go", "ruby", "php", "r", "scala", "bash", "html", "css",
    # Data & ML
    "pandas", "numpy", "matplotlib", "seaborn", "tableau", "power bi", "excel", "scikit-learn",
    "pytorch", "tensorflow", "keras", "opencv", "spacy", "nltk", "langchain", "langgraph",
    "spark", "hadoop", "airflow", "dbt", "kafka",
    # Databases & Cloud
    "postgresql", "mysql", "sqlite", "mongodb", "redis", "cassandra", "snowflake", "bigquery", "redshift",
    "aws", "azure", "gcp", "docker", "kubernetes", "linux", "git", "github",
    # Web & Backend
    "fastapi", "flask", "django", "react", "next.js", "node.js", "express", "graphql", "rest apis"
]


def extract_skills_from_text(text: str) -> List[str]:
    """
    Deterministically extracts explicitly present skills from raw resume text.
    NEVER infers or invents skills.
    """
    if not text:
        return []

    text_lower = text.lower()
    found_skills = []

    for skill in KNOWN_SKILLS:
        # Match whole word / phrase boundaries
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            # Format nicely
            found_skills.append(skill.title() if len(skill) > 3 and skill not in ["sql", "aws", "gcp"] else skill.upper() if skill in ["sql", "aws", "gcp", "dbt", "r"] else skill)

    return sorted(list(set(found_skills)))


def extract_education_from_text(text: str) -> List[str]:
    """
    Extracts degrees and universities mentioned in the text.
    """
    degrees = []
    degree_patterns = [
        r"(?:B\.Tech|B\.E\.|Bachelor(?:'s)?|B\.Sc|BS|M\.Tech|M\.S\.|Master(?:'s)?|Ph\.D|Diploma)\s*(?:in\s+[A-Za-z\s]+)?",
        r"(?:Anna University|IIT|NIT|BITS|University of [A-Za-z\s]+|[A-Za-z\s]+ University)"
    ]
    for p in degree_patterns:
        matches = re.findall(p, text, re.IGNORECASE)
        for m in matches:
            clean = m.strip().split("\n")[0]
            if len(clean) > 3 and clean not in degrees:
                degrees.append(clean)
    return degrees


try:
    from langchain_core.tools import tool

    @tool
    def extract_resume_skills_tool(resume_text: str) -> str:
        """
        Extract explicitly stated technical skills from candidate resume text.
        Guaranteed zero fabrication - never returns skills absent from the text.
        """
        skills = extract_skills_from_text(resume_text)
        return json.dumps({"skills": skills, "count": len(skills)}, indent=2)

except ImportError:
    class MockExtractTool:
        def __init__(self):
            self.__name__ = "extract_resume_skills_tool"
            self.__doc__ = "Extract explicitly stated technical skills from resume text."

        def invoke(self, input_data: Any) -> str:
            if isinstance(input_data, dict):
                text = input_data.get("resume_text", "")
            else:
                text = str(input_data)
            skills = extract_skills_from_text(text)
            return json.dumps({"skills": skills, "count": len(skills)}, indent=2)

    extract_resume_skills_tool = MockExtractTool()


__all__ = ["extract_skills_from_text", "extract_education_from_text", "extract_resume_skills_tool"]
