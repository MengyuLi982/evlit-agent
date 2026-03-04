from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetrievalProfile:
    name: str
    description: str
    focus_tracks: tuple[str, ...]
    positive_terms: tuple[str, ...]
    negative_terms: tuple[str, ...]
    source_weights: dict[str, float]
    default_year_from: int
    default_min_score: float
    default_min_evidence: int


SPS_SPACE_EVENT_STARTRACKING = RetrievalProfile(
    name="sps_space_event_startracking",
    description=(
        "TUM SPS-oriented Event Camera literature profile focused on star tracking, "
        "attitude determination, and spacecraft jitter robustness."
    ),
    focus_tracks=(
        "star tracking",
        "attitude determination",
        "spacecraft jitter",
        "satellite detection",
    ),
    positive_terms=(
        "event camera",
        "event-based vision",
        "neuromorphic",
        "dvs",
        "davis",
        "star tracking",
        "star tracker",
        "attitude determination",
        "attitude estimation",
        "spacecraft jitter",
        "satellite detection",
        "space situational awareness",
        "resident space object",
        "onboard satellite operation",
        "weltraumbeobachtung",
        "raumfahrtsystemtechnik",
        "satellitenbetrieb",
    ),
    negative_terms=(
        "brain tumor",
        "pedestrian",
        "sentiment analysis",
        "uav civil",
        "genomics",
        "medical imaging",
    ),
    source_weights={
        "arxiv": 1.0,
        "openalex": 0.9,
        "semanticscholar": 0.7,
        "crossref": 0.5,
    },
    default_year_from=2021,
    default_min_score=0.55,
    default_min_evidence=3,
)


DEFAULT_PROFILE = SPS_SPACE_EVENT_STARTRACKING

_PROFILE_REGISTRY: dict[str, RetrievalProfile] = {
    SPS_SPACE_EVENT_STARTRACKING.name: SPS_SPACE_EVENT_STARTRACKING,
}


def get_profile(name: str | None) -> RetrievalProfile:
    if not name:
        return DEFAULT_PROFILE
    return _PROFILE_REGISTRY.get(name, DEFAULT_PROFILE)


def list_profiles() -> list[RetrievalProfile]:
    return list(_PROFILE_REGISTRY.values())
