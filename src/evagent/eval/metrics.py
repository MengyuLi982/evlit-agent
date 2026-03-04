from __future__ import annotations

import math


def recall_at_k(relevant: set[str], predicted: list[str], k: int) -> float:
    if not relevant:
        return 0.0
    hit = len(relevant.intersection(predicted[:k]))
    return hit / len(relevant)


def mrr_at_k(relevant: set[str], predicted: list[str], k: int) -> float:
    for idx, item in enumerate(predicted[:k], start=1):
        if item in relevant:
            return 1.0 / idx
    return 0.0


def ndcg_at_k(relevant: set[str], predicted: list[str], k: int) -> float:
    dcg = 0.0
    for idx, item in enumerate(predicted[:k], start=1):
        rel = 1.0 if item in relevant else 0.0
        dcg += rel / math.log2(idx + 1)

    ideal_hits = min(len(relevant), k)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, ideal_hits + 1))
    if idcg == 0:
        return 0.0
    return dcg / idcg
