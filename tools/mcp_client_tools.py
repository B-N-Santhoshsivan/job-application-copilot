"""
LangChain tool adapters around the custom MCP server tools.
Enables LangGraph agents and ReAct loops to call the MCP tools directly.
"""

import json
from typing import Any, Optional
from mcp_server.server import search_jobs, save_application, write_file

try:
    from langchain_core.tools import tool

    @tool
    def search_jobs_tool(role: str = "", location: str = "", keywords: str = "") -> str:
        """
        Search available job openings matching role, location, or keywords in mock repository.
        Returns a JSON string list of job descriptions, required skills, and salary benchmarks.
        """
        results = search_jobs(role=role, location=location, keywords=keywords)
        return json.dumps(results, indent=2)

    @tool
    def save_application_tool(
        company: str,
        role: str,
        application_date: str = "",
        status: str = "Interested",
        notes: str = ""
    ) -> str:
        """
        Record or update a job application entry in SQLite application tracker.
        """
        result = save_application(
            company=company,
            role=role,
            application_date=application_date,
            status=status,
            notes=notes
        )
        return json.dumps(result, indent=2)

    @tool
    def write_file_tool(filename: str, content: str) -> str:
        """
        Save a generated document (such as a tailored cover letter or interview prep guide)
        safely to outputs/ on the local file system.
        """
        result = write_file(filename=filename, content=content)
        return json.dumps(result, indent=2)

except ImportError:
    class MockMCPTool:
        def __init__(self, fn):
            self.fn = fn
            self.__name__ = fn.__name__
            self.__doc__ = fn.__doc__

        def __call__(self, *args, **kwargs):
            return self.fn(*args, **kwargs)

        def invoke(self, input_data: Any) -> str:
            if isinstance(input_data, dict):
                return json.dumps(self.fn(**input_data), indent=2)
            return json.dumps(self.fn(input_data), indent=2)

    search_jobs_tool = MockMCPTool(lambda role="", location="", keywords="": search_jobs(role, location, keywords))
    save_application_tool = MockMCPTool(lambda company, role, application_date="", status="Interested", notes="": save_application(company, role, application_date, status, notes))
    write_file_tool = MockMCPTool(write_file)

__all__ = ["search_jobs_tool", "save_application_tool", "write_file_tool"]
