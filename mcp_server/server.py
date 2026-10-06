"""
Custom Model Context Protocol (MCP) Server for Job Application Copilot.
Implements the 3 mandatory tools:
1. search_jobs: Search job openings by role and location.
2. save_application: Log and track application status in SQLite.
3. write_file: Safely persist cover letters, interview sheets, and analysis notes to disk.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from mcp_server.tools.search_jobs import search_jobs
from mcp_server.tools.save_application import save_application, get_applications
from mcp_server.tools.write_file import write_file, read_output_file

# ==========================================
# FastMCP Server Registration (Standard MCP)
# ==========================================
try:
    from mcp.server.fastmcp import FastMCP
    mcp_app = FastMCP("job-application-copilot-mcp")

    @mcp_app.tool()
    def mcp_search_jobs(role: str = "", location: str = "", keywords: str = "") -> str:
        """Search job listings matching a role, location, or keywords."""
        return json.dumps(search_jobs(role, location, keywords), indent=2)

    @mcp_app.tool()
    def mcp_save_application(
        company: str,
        role: str,
        application_date: str = "",
        status: str = "Interested",
        notes: str = ""
    ) -> str:
        """Record an application with company, role, date, status, and notes in SQLite."""
        return json.dumps(save_application(company, role, application_date, status, notes), indent=2)

    @mcp_app.tool()
    def mcp_write_file(filename: str, content: str) -> str:
        """Saves generated documents (e.g., cover letters) to disk."""
        return json.dumps(write_file(filename, content), indent=2)

except ImportError:
    mcp_app = None


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio" and mcp_app is not None:
        print("Starting Job Application Copilot MCP Server via stdio...", file=sys.stderr)
        mcp_app.run()
    else:
        print("Job Application Copilot MCP Server verification:")
        test_jobs = search_jobs("Data Analyst")
        print(f"✓ search_jobs found {len(test_jobs)} listings")
        test_app = save_application("Zoho Corporation", "Data Analyst", status="Interview", notes="MCP test")
        print(f"✓ save_application: {test_app.get('message')}")
        test_file = write_file("test_mcp_run.txt", "Verified MCP file output.")
        print(f"✓ write_file: {test_file.get('message')}")
