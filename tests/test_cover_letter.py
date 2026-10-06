"""
Test Suite: Cover Letter Generation and MCP Persistence.
Satisfies Section 17 requirement 10.
"""

import os
import unittest
from agents.cover_letter import cover_letter_node
from graph.state import create_initial_state
from mcp_server.tools.write_file import OUTPUT_DIR


class TestCoverLetterAgent(unittest.TestCase):
    def test_cover_letter_generation_and_saving(self):
        state = create_initial_state(
            resume_text="SANTHOSH SIVAN\nB.Tech Computer Science Anna University\nSkills: Python, SQL, Tableau\nProjects: E-Commerce Sales Dashboard\nExperience: Data Analytics Intern at TechSphere Solutions",
            job_description="Company: Zoho Corporation\nRole: Junior Data Analyst",
            candidate_name="Santhosh Sivan",
            target_company="Zoho Corporation",
            target_role="Junior Data Analyst"
        )

        res = cover_letter_node(state)
        cover_letter = res.get("cover_letter", "")
        self.assertTrue(len(cover_letter) > 100)

        # Verify word count is reasonable (within ~250 - 500 range)
        words = len(cover_letter.split())
        self.assertGreaterEqual(words, 200, "Cover letter too brief")
        self.assertLessEqual(words, 550, "Cover letter too verbose")

        # Verify file output saved via MCP write_file
        output_files = res.get("output_files", [])
        self.assertTrue(len(output_files) > 0)
        expected_filename = "Santhosh_Sivan_Zoho_Corporation_cover_letter.txt"
        self.assertTrue(os.path.exists(OUTPUT_DIR / expected_filename))


if __name__ == "__main__":
    unittest.main()
