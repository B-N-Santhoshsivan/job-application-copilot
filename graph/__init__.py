"""
Graph package initialization with lazy graph resolution to avoid circular imports.
"""

from graph.state import JobCopilotState, create_initial_state, initial_state

def __getattr__(name):
    if name in ("copilot_graph", "build_copilot_graph"):
        from graph.workflow import copilot_graph, build_copilot_graph
        if name == "copilot_graph":
            return copilot_graph
        return build_copilot_graph
    raise AttributeError(f"module 'graph' has no attribute {name!r}")

__all__ = ["JobCopilotState", "create_initial_state", "initial_state", "copilot_graph", "build_copilot_graph"]
