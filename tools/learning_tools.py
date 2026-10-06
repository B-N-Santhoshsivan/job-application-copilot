"""
Learning Resources and Skill-Gap Recommendation Tool.
Second custom LangChain tool satisfying course requirements.
"""

from typing import Dict, List, Any

# Curated repository of verified learning resources & courses
SKILL_LEARNING_REPO: Dict[str, Dict[str, str]] = {
    "tableau": {
        "title": "Tableau Desktop Specialist & Visual Analytics",
        "platform": "Tableau Public / Coursera",
        "duration": "15-20 hours",
        "url": "https://www.tableau.com/learn/training",
        "description": "Hands-on projects covering LOD expressions, dashboard design, calculated fields, and KPI parameter controls."
    },
    "power bi": {
        "title": "Microsoft Power BI Data Analyst (PL-300)",
        "platform": "Microsoft Learn (Free)",
        "duration": "25 hours",
        "url": "https://learn.microsoft.com/en-us/credentials/certifications/data-analyst-associate/",
        "description": "DAX formulas, Power Query M transformations, data modeling, and enterprise report publishing."
    },
    "snowflake": {
        "title": "Snowflake Hands-on Essentials & Data Warehousing",
        "platform": "Snowflake University (Free)",
        "duration": "10-15 hours",
        "url": "https://learn.snowflake.com",
        "description": "Zero-copy cloning, virtual warehouses, SnowSQL, semi-structured JSON querying, and data sharing."
    },
    "airflow": {
        "title": "Apache Airflow Fundamentals for Data Engineering",
        "platform": "Astronomer Academy",
        "duration": "8-12 hours",
        "url": "https://academy.astronomer.io",
        "description": "Building Directed Acyclic Graphs (DAGs), operators, task dependencies, sensor patterns, and scheduling."
    },
    "docker": {
        "title": "Docker for Developers & Containerization",
        "platform": "Docker Official Docs / FreeCodeCamp",
        "duration": "10 hours",
        "url": "https://docs.docker.com/get-started/",
        "description": "Dockerfiles, multi-stage builds, docker-compose orchestration, volume persistence, and networking."
    },
    "langchain": {
        "title": "DeepLearning.AI: LangChain & Multi-Agent Systems with LangGraph",
        "platform": "DeepLearning.AI (Free)",
        "duration": "8 hours",
        "url": "https://www.deeplearning.ai/short-courses/",
        "description": "Stateful agents, tool-calling ReAct loops, prompt schemas, and memory checkpointing."
    },
    "sql": {
        "title": "Advanced SQL for Data Science & Analytics",
        "platform": "Mode Analytics SQL Tutorial / LeetCode Database",
        "duration": "15 hours",
        "url": "https://mode.com/sql-tutorial/",
        "description": "Window functions (ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD), CTEs, query plan optimization, indexing."
    },
    "aws": {
        "title": "AWS Cloud Practitioner & Cloud Fundamentals",
        "platform": "AWS Skill Builder (Free)",
        "duration": "12 hours",
        "url": "https://skillbuilder.aws",
        "description": "S3 object storage, EC2 compute, IAM security, RDS databases, and serverless Lambda functions."
    }
}


def _lookup_resource(skill_name: str) -> str:
    skill_clean = str(skill_name).lower().strip()

    for key, data in SKILL_LEARNING_REPO.items():
        if key in skill_clean or skill_clean in key:
            return (
                f"[Source: Verified Learning Database]\n"
                f"Recommended Course: {data['title']}\n"
                f"Platform: {data['platform']}\n"
                f"Estimated Effort: {data['duration']}\n"
                f"Curriculum Focus: {data['description']}\n"
                f"Official Link: {data['url']}"
            )

    return (
        f"[Source: Developer Learning Path for '{skill_name}']\n"
        f"Recommended Action: Complete official documentation quickstarts and build a dedicated GitHub mini-project for {skill_name}.\n"
        f"Suggested Platform: FreeCodeCamp / YouTube technical walkthroughs / Official Documentation.\n"
        f"Estimated Effort: 10-14 hours of deliberate coding practice."
    )


try:
    from langchain_core.tools import tool

    @tool
    def find_learning_resources(skill_name: str) -> str:
        """
        Search for recommended free courses, documentation, and hands-on learning resources
        for a missing technical skill or gap identified during job analysis.

        Args:
            skill_name: Name of the skill to learn (e.g., 'Snowflake', 'Airflow', 'Tableau', 'Docker')
        """
        return _lookup_resource(skill_name)

except ImportError:
    class MockTool:
        def __init__(self, fn):
            self.fn = fn
            self.__name__ = fn.__name__
            self.__doc__ = fn.__doc__

        def __call__(self, *args, **kwargs):
            return self.fn(*args, **kwargs)

        def invoke(self, input_data: Any) -> str:
            if isinstance(input_data, dict):
                skill = input_data.get("skill_name") or next(iter(input_data.values()), "")
                return self.fn(skill)
            return self.fn(str(input_data))

    def _dummy_func(skill_name: str) -> str:
        return _lookup_resource(skill_name)

    find_learning_resources = MockTool(_dummy_func)

# Alias for backwards compatibility
find_learning_resources_tool = find_learning_resources
