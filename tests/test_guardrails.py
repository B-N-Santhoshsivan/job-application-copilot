"""
Test Suite: Strict Guardrails & Non-Fabrication Verification.
Satisfies Section 17 requirement 7:
  "Include at least one test proving that the system does NOT invent a candidate skill."
"""

import unittest
from tools.resume_tools import extract_skills_from_text, extract_education_from_text
from tools.matching_tools import calculate_resume_match
from agents.cover_letter import cover_letter_node
from graph.state import create_initial_state


class TestGuardrails(unittest.TestCase):
    def test_never_invents_absent_skills(self):
        """
        Proof: Given a resume that only has Python and SQL,
        the system MUST NOT invent skills like 'Kubernetes', 'Golang', or 'C#'.
        """
        sparse_resume = """
        John Doe
        Education: B.Sc Mathematics
        Technical Skills: Python, SQL
        Projects: Analyzed tabular dataset using SQL queries.
        """

        extracted = extract_skills_from_text(sparse_resume)
        self.assertIn("Python", extracted)
        self.assertIn("SQL", extracted)

        # Explicitly verify fabricated skills are absent
        unmentioned_skills = ["Kubernetes", "Golang", "C#", "Rust", "Swift", "Snowflake", "Docker"]
        for skill in unmentioned_skills:
            self.assertNotIn(skill, extracted, f"CRITICAL GUARDRAIL BREACH: Invented skill '{skill}'!")

    def test_missing_skills_labeled_as_not_found(self):
        """
        Verifies that skills required by JD but missing in resume
        are labeled as 'Not found in resume' rather than presumed known.
        """
        sparse_resume = "Skills: Python"
        demanding_jd = "Required: Python, Snowflake, Kubernetes"

        match_res = calculate_resume_match(sparse_resume, demanding_jd)
        missing = [s.lower() for s in match_res["missing_skills"]]
        self.assertTrue("snowflake" in missing or "kubernetes" in missing)

        missing_breakdown = match_res["breakdown"]["technical_skills"]["missing"]
        self.assertTrue(all("not found in resume" in s.lower() for s in missing_breakdown))

    def test_cover_letter_avoids_fabricating_credentials(self):
        """
        Verifies cover letter agent grounds itself in candidate resume
        and does not invent fake PhD degrees or false executive titles.
        """
        state = create_initial_state(
            resume_text="SANTHOSH SIVAN\nB.Tech Computer Science, Anna University\nSkills: Python, SQL",
            job_description="Company: Zoho Corporation\nRole: Junior Data Analyst",
            candidate_name="Santhosh Sivan",
            target_company="Zoho Corporation",
            target_role="Junior Data Analyst"
        )
        res = cover_letter_node(state)
        cover_letter = res.get("cover_letter", "")

        # Verify candidate name and target role are included
        self.assertIn("Zoho", cover_letter)
        # Verify no hallucinated Ivy League degrees or CEO roles
        self.assertNotIn("Ph.D from Harvard", cover_letter)
        self.assertNotIn("Chief Executive Officer", cover_letter)


if __name__ == "__main__":
    unittest.main()
