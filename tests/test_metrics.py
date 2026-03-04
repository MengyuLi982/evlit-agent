from evagent.eval.metrics import mrr_at_k, ndcg_at_k, recall_at_k


def test_recall_at_k() -> None:
    assert recall_at_k({"a", "b"}, ["c", "a", "b"], 2) == 0.5


def test_mrr_at_k() -> None:
    assert mrr_at_k({"a", "b"}, ["c", "b", "a"], 3) == 0.5


def test_ndcg_at_k_bounds() -> None:
    score = ndcg_at_k({"a", "b"}, ["a", "c", "b"], 3)
    assert 0.0 <= score <= 1.0
