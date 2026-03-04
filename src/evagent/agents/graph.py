from __future__ import annotations

from typing import Any

try:
    from langgraph.graph import END, START, StateGraph
except Exception:  # pragma: no cover - optional dependency fallback
    END = "__end__"
    START = "__start__"
    StateGraph = None  # type: ignore[assignment]

from evagent.agents.nodes import (
    critic_and_fix,
    draft_answer,
    extract_evidence,
    plan_subquestions,
    retrieve_candidates,
)
from evagent.agents.state import AgentState
from evagent.llm.client import LLMClient
from evagent.sources import MultiSourceRetriever


def build_graph(retriever: MultiSourceRetriever, llm: LLMClient):
    if StateGraph is None:
        class _FallbackGraph:
            def invoke(self, state: dict[str, Any]) -> dict[str, Any]:
                state = {**state, **plan_subquestions(state)}
                state = {**state, **retrieve_candidates(state, retriever)}
                state = {**state, **extract_evidence(state)}
                critic = critic_and_fix(state)
                state = {**state, **critic}
                if state.get("needs_more"):
                    state = {**state, **retrieve_candidates(state, retriever)}
                    state = {**state, **extract_evidence(state)}
                state = {**state, **draft_answer(state, llm)}
                return state

        return _FallbackGraph()

    graph = StateGraph(AgentState)

    graph.add_node("plan", plan_subquestions)
    graph.add_node("retrieve", lambda s: retrieve_candidates(s, retriever))
    graph.add_node("evidence", extract_evidence)
    graph.add_node("critic", critic_and_fix)
    graph.add_node("draft", lambda s: draft_answer(s, llm))

    graph.add_edge(START, "plan")
    graph.add_edge("plan", "retrieve")
    graph.add_edge("retrieve", "evidence")
    graph.add_edge("evidence", "critic")

    def route_after_critic(state: AgentState) -> str:
        if state.get("needs_more"):
            return "retrieve"
        return "draft"

    graph.add_conditional_edges("critic", route_after_critic, {"retrieve": "retrieve", "draft": "draft"})
    graph.add_edge("draft", END)

    return graph.compile()
