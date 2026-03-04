from evagent.domain import get_profile
from evagent.models import PaperRecord
from evagent.retrieval import profile_filter_and_rank


def test_profile_filter_and_rank_keeps_relevant_record() -> None:
    profile = get_profile("sps_space_event_startracking")
    records = [
        PaperRecord(
            source="arxiv",
            paper_id="arxiv:1",
            title="Event camera star tracking for spacecraft jitter compensation",
            abstract="Attitude determination for satellite operations with neuromorphic vision.",
            year=2024,
        ),
        PaperRecord(
            source="openalex",
            paper_id="openalex:1",
            title="Brain tumor segmentation for medical imaging",
            abstract="No space topic here.",
            year=2024,
        ),
    ]

    ranked, stats = profile_filter_and_rank(records, profile, year_from=2021, min_score=0.55)

    assert len(ranked) == 1
    assert ranked[0].paper_id == "arxiv:1"
    assert float(ranked[0].metadata["retrieval_score"]) >= 0.55
    assert stats["raw_count"] == 2
    assert stats["after_score_filter"] == 1


def test_profile_filter_drops_crossref_component() -> None:
    profile = get_profile("sps_space_event_startracking")
    records = [
        PaperRecord(
            source="crossref",
            paper_id="crossref:component",
            title="Event camera star tracking",
            abstract="spacecraft attitude estimation",
            year=2025,
            metadata={"type": "component"},
        )
    ]

    ranked, stats = profile_filter_and_rank(records, profile, year_from=2021, min_score=0.1)
    assert ranked == []
    assert stats["after_component_filter"] == 0
