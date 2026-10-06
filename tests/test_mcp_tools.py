"""
Test Suite: Custom MCP Server Tools.
Satisfies Section 17 requirements 4, 5, 6:
  - MCP search_jobs (20+ dataset validation)
  - MCP save_application (SQLite persistence)
  - MCP write_file (Safe output writing)
"""

import os
import unittest
from mcp_server.tools.search_jobs import search_jobs, load_jobs
from mcp_server.tools.save_application import save_application, get_applications
from mcp_server.tools.write_file import write_file, read_output_file


class TestMCPTools(unittest.TestCase):
    def test_search_jobs_catalog_size(self):
        """Validates that dataset contains at least 20 mock listings with required schema."""
        all_jobs = load_jobs()
        self.assertGreaterEqual(len(all_jobs), 20, "Must contain at least 20 mock job listings")

        required_keys = ["job_id", "company", "role", "location", "description", "required_skills", "preferred_skills", "experience", "employment_type"]
        for job in all_jobs:
            for k in required_keys:
                self.assertIn(k, job, f"Job {job.get('job_id')} is missing field '{k}'")

    def test_search_jobs_filtering(self):
        """Validates search filtering by role and location."""
        analyst_jobs = search_jobs(role="Data Analyst")
        self.assertGreater(len(analyst_jobs), 0)
        self.assertTrue(any("analyst" in j["role"].lower() for j in analyst_jobs))

        chennai_jobs = search_jobs(location="Chennai")
        self.assertGreater(len(chennai_jobs), 0)
        self.assertTrue(all("chennai" in j["location"].lower() for j in chennai_jobs))

    def test_save_application_sqlite(self):
        """Validates storing application records in SQLite data/applications.db."""
        res = save_application(
            company="Zoho Corporation",
            role="Junior Data Analyst",
            status="Interview",
            notes="Automated test verification note"
        )
        self.assertTrue(res.get("success"))
        self.assertIn("application", res)
        app_record = res["application"]
        self.assertEqual(app_record["company"], "Zoho Corporation")
        self.assertEqual(app_record["status"], "Interview")

        # Verify record exists in database
        recent_apps = get_applications(limit=10)
        self.assertTrue(any(a["id"] == app_record["id"] for a in recent_apps))

    def test_write_file_safe_persistence(self):
        """Validates writing generated document to outputs/ directory safely."""
        test_filename = "test_verification_doc.txt"
        test_content = "Verified document written by Custom MCP write_file tool."

        res = write_file(test_filename, test_content)
        self.assertTrue(res.get("success"))
        self.assertTrue(os.path.exists(res["filepath"]))

        read_back = read_output_file(test_filename)
        self.assertEqual(read_back, test_content)


if __name__ == "__main__":
    unittest.main()
