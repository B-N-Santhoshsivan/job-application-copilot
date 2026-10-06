"""
Test Suite: Resume Skill Extraction and Explainable Match Scoring.
Satisfies Section 17 requirements 1, 2, 3.
"""

import unittest
from tools.resume_tools import extract_skills_from_text, extract_education_from_text
from tools.matching_tools import calculate_resume_match, DEFAULT_WEIGHTS


class TestResumeAnalyzer(unittest.TestCase):
    def setUp(self):
        self.sample_resume = """
        SANTHOSH SIVAN
        EDUCATION: B.Tech in Computer Science and Engineering, Anna University
        TECHNICAL SKILLS: Python, SQL (PostgreSQL), Tableau, Pandas, Scikit-Learn
        PROJECTS: E-Commerce Sales Dashboard analyzing 150,000 records
        EXPERIENCE: Data Analytics Intern at TechSphere Solutions
        CERTIFICATIONS: Google Data Analytics Certificate
        """
        self.sample_jd = """
        Company: Zoho Corporation
        Role: Junior Data Analyst
        MINIMUM QUALIFICATIONS: Python, SQL, Tableau
        PREFERRED QUALIFICATIONS: Snowflake, Airflow, BigQuery
        """

    def test_resume_skill_extraction(self):
        """Test 1: Factual resume skill extraction."""
        skills = extract_skills_from_text(self.sample_resume)
        self.assertIn("Python", skills)
        self.assertIn("SQL", skills)
        self.assertIn("Tableau", skills)
        self.assertIn("Pandas", skills)
        # Verify unmentioned skills are NOT extracted
        self.assertNotIn("Rust", skills)
        self.assertNotIn("Golang", skills)

    def test_resume_matching_and_scoring(self):
        """Test 2: Explainable 5-dimension weighted match scoring."""
        result = calculate_resume_match(self.sample_resume, self.sample_jd)
        self.assertIn("match_score", result)
        self.assertTrue(0 <= result["match_score"] <= 100)
        self.assertIn("breakdown", result)

        breakdown = result["breakdown"]
        self.assertIn("technical_skills", breakdown)
        self.assertIn("experience", breakdown)
        self.assertIn("education", breakdown)
        self.assertIn("projects", breakdown)
        self.assertIn("certifications", breakdown)

        # Verify default weights sum to 100%
        self.assertEqual(DEFAULT_WEIGHTS["technical_skills"], 0.40)
        self.assertEqual(DEFAULT_WEIGHTS["experience"], 0.25)
        self.assertEqual(DEFAULT_WEIGHTS["education"], 0.15)
        self.assertEqual(DEFAULT_WEIGHTS["projects"], 0.10)
        self.assertEqual(DEFAULT_WEIGHTS["certifications"], 0.10)

    def test_missing_skill_detection(self):
        """Test 3: Missing skills detection with explicit non-hallucination labeling."""
        result = calculate_resume_match(self.sample_resume, self.sample_jd)
        matching = [s.lower() for s in result["matching_skills"]]
        missing = [s.lower() for s in result["missing_skills"]]

        self.assertIn("python", matching)
        self.assertIn("sql", matching)
        self.assertIn("tableau", matching)

        # Snowflake & Airflow should be detected as missing from resume
        self.assertTrue(any(s in missing for s in ["snowflake", "airflow", "bigquery"]))


if __name__ == "__main__":
    unittest.main()
