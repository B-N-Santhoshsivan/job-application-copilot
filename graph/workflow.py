"""
LangGraph Multi-Agent Orchestration Workflow for Job Application Copilot.
Coordinates 7 specialized agents:
  1. Supervisor
  2. Resume Analyzer
  3. Skill Gap ReAct Agent
  4. Company Research Agent (Tavily)
  5. Cover Letter Agent
  6. Interview Prep Agent
  7. Final Report Agent
"""

from typing import Dict, Any, Literal

try:
    from langgraph.graph import StateGraph, END
except ImportError:
    END = "__END__"

    class StateGraph:
        def __init__(self, state_schema):
            self.state_schema = state_schema
            self.nodes = {}
            self.entry_point = None
            self.edges = {}
            self.conditional_edges = {}

        def add_node(self, name, node_func):
            self.nodes[name] = node_func

        def set_entry_point(self, name):
            self.entry_point = name

        def add_edge(self, start_key, end_key):
            self.edges[start_key] = end_key

        def add_conditional_edges(self, source, path_func, path_map):
            self.conditional_edges[source] = (path_func, path_map)

        def compile(self):
            return CompiledGraph(self)

    class CompiledGraph:
        def __init__(self, graph):
            self.graph = graph

        def invoke(self, initial_state):
            current_state = dict(initial_state)
            current_node = self.graph.entry_point
            steps = 0
            visited = []
            while current_node and current_node != END and steps < 25:
                steps += 1
                visited.append(current_node)
                fn = self.graph.nodes.get(current_node)
                if fn:
                    updates = fn(current_state)
                    if isinstance(updates, dict):
                        current_state.update(updates)

                # Route to next node
                if current_node in self.graph.conditional_edges:
                    routing_fn, path_map = self.graph.conditional_edges[current_node]
                    next_choice = routing_fn(current_state)
                    current_node = path_map.get(next_choice, END)
                elif current_node in self.graph.edges:
                    current_node = self.graph.edges[current_node]
                else:
                    break
            return current_state


from graph.state import JobCopilotState
from agents.supervisor import supervisor_node
from agents.resume_analyzer import resume_analyzer_node
from agents.skill_gap import skill_gap_node
from agents.company_research import company_research_node
from agents.cover_letter import cover_letter_node
from agents.interview_prep import interview_prep_node
from agents.final_report import final_report_node


def route_from_supervisor(state: JobCopilotState) -> str:
    """
    Decides routing based on intent classification from Supervisor.
    """
    next_step = state.get("next_step", "RESUME_ANALYZER")

    if next_step == "INTERVIEW_PREP":
        return "interview_prep"
    elif next_step == "COVER_LETTER":
        return "company_research"
    elif next_step == "SKILL_GAP":
        return "skill_gap"
    else:
        return "resume_analyzer"


def build_copilot_graph():
    """
    Constructs and compiles the multi-agent StateGraph.
    """
    builder = StateGraph(JobCopilotState)

    # 1. Register all 7 agent nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("resume_analyzer", resume_analyzer_node)
    builder.add_node("skill_gap", skill_gap_node)
    builder.add_node("company_research", company_research_node)
    builder.add_node("cover_letter", cover_letter_node)
    builder.add_node("interview_prep", interview_prep_node)
    builder.add_node("final_report", final_report_node)

    # 2. Set entry point
    builder.set_entry_point("supervisor")

    # 3. Conditional routing from supervisor
    builder.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "resume_analyzer": "resume_analyzer",
            "skill_gap": "skill_gap",
            "company_research": "company_research",
            "interview_prep": "interview_prep",
        }
    )

    # 4. Sequential pipeline edges for full workflow
    builder.add_edge("resume_analyzer", "skill_gap")
    builder.add_edge("skill_gap", "company_research")
    builder.add_edge("company_research", "cover_letter")
    builder.add_edge("cover_letter", "interview_prep")
    builder.add_edge("interview_prep", "final_report")
    builder.add_edge("final_report", END)

    return builder.compile()


# Singleton compiled graph instance
copilot_graph = build_copilot_graph()

__all__ = ["build_copilot_graph", "copilot_graph"]
