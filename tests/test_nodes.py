from evagent.agents.nodes import critic_and_fix, draft_answer, extract_evidence, plan_subquestions


class _DummyLLM:
    def summarize_evidence(self, query: str, evidence: list[dict]) -> str:
        return f"ok:{query}:{len(evidence)}"


def test_planner_adds_sps_subqueries() -> None:
    out = plan_subquestions({"query": "event camera", "profile_name": "sps_space_event_startracking"})
    assert len(out["subqueries"]) >= 4
    assert any("spacecraft jitter" in q for q in out["subqueries"])


def test_extract_evidence_from_abstract() -> None:
    state = {
        "query": "x",
        "candidates": [
            {
                "paper_id": "p1",
                "title": "Paper",
                "abstract": "This is abstract",
                "metadata": {"retrieval_score": 0.9, "matched_terms": ["star tracking"]},
            },
        ],
    }
    out = extract_evidence(state)
    assert len(out["evidence"]) == 1
    assert out["evidence"][0]["confidence"] == 0.9


def test_critic_requests_retry_when_evidence_is_low() -> None:
    out = critic_and_fix({"evidence": [], "retry_count": 0, "min_evidence": 3})
    assert out["needs_more"] is True
    assert out["retry_count"] == 1


def test_critic_stops_after_one_retry() -> None:
    out = critic_and_fix({"evidence": [], "retry_count": 1, "min_evidence": 3})
    assert out["needs_more"] is False
    assert out["retry_count"] == 1


def test_draft_answer_returns_insufficient_message() -> None:
    out = draft_answer(
        {
            "query": "q",
            "profile_name": "sps_space_event_startracking",
            "min_evidence": 3,
            "evidence": [{"paper_id": "p1"}],
        },
        _DummyLLM(),
    )
    assert "Evidence is insufficient" in out["answer"]


def test_draft_answer_uses_llm_when_evidence_is_enough() -> None:
    out = draft_answer(
        {
            "query": "q",
            "min_evidence": 1,
            "evidence": [{"paper_id": "p1"}],
        },
        _DummyLLM(),
    )
    assert out["answer"].startswith("ok:q:1")
