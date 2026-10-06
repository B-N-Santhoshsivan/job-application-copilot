"""
Test Suite: LangGraph Multi-Agent Orchestration Workflow.
Satisfies Section 17 requirement 8.
"""

import unittest
from graph.workflow import copilot_graph
from graph.state import create_initial_state


class TestLangGraphWorkflow(unittest.TestCase):
    def setUp(self):
        self.sample_resume = """
        SANTHOSH SIVAN
        Chennai, India | santhosh@example.com
        EDUCATION: B.Tech Computer Science, Anna University (CGPA: 8.7/10)
        TECHNICAL SKILLS: Python, SQL, Tableau, Pandas, Scikit-Learn
        PROJECTS: E-Commerce Sales Performance Dashboard analyzing 150,000 transactions
        EXPERIENCE: Data Analytics Intern at TechSphere Solutions
        CERTIFICATIONS: Google Data Analytics Certificate
        """
        self.sample_jd = """
        Company: Zoho Corporation
        Role: Junior Data Analyst
        MINIMUM QUALIFICATIONS: Python, SQL, Tableau
        PREFERRED QUALIFICATIONS: Snowflake, Airflow
        """

    def test_full_workflow_execution(self):
        """Validates that all 7 agents execute in sequence and populate shared state."""
        state = create_initial_state(
            resume_text=self.sample_resume,
            job_description=self.sample_jd,
            user_query="Perform full evaluation and generate application package",
            candidate_name="Santhosh Sivan",
            target_company="Zoho Corporation",
            target_role="Junior Data Analyst"
        )

        final_state = copilot_graph.invoke(state)

        # 1. State metadata populated
        self.assertEqual(final_state["candidate_name"], "Santhosh Sivan")
        self.assertEqual(final_state["target_company"], "Zoho Corporation")

        # 2. Resume Analyzer
        self.assertTrue(bool(final_state.get("match_analysis")))
        self.assertGreater(final_state.get("match_score", 0), 0)

        # 3. Skill Gap Agent
        self.assertTrue(bool(final_state.get("skill_gaps")))

        # 4. Company Research Agent
        self.assertTrue(bool(final_state.get("company_research")))

        # 5. Cover Letter Agent
        self.assertTrue(bool(final_state.get("cover_letter")))

        # 6. Interview Prep Agent
        self.assertTrue(bool(final_state.get("interview_sheet")))

        # 7. Final Report Agent
        self.assertTrue(bool(final_state.get("final_report")))

        # 8. MCP write_file persistence
        output_files = final_state.get("output_files", [])
        self.assertGreaterEqual(len(output_files), 2, "Expected at least cover letter and interview guide saved")


if __name__ == "__main__":
    unittest.main()
