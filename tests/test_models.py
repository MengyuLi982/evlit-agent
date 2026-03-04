from evagent.models import PaperRecord, dedup_key


def test_dedup_key_prefers_doi() -> None:
    p = PaperRecord(source="x", paper_id="id", title="A", doi="10.1000/xyz")
    assert dedup_key(p) == "doi:10.1000/xyz"


def test_dedup_key_arxiv() -> None:
    p = PaperRecord(source="x", paper_id="arxiv:1234.5678", title="A")
    assert dedup_key(p) == "arxiv:1234.5678"


def test_dedup_key_fallback() -> None:
    p = PaperRecord(source="x", paper_id="s2:1", title="My Paper", authors=["Alice"], year=2024)
    assert dedup_key(p).startswith("fallback:my paper|alice|2024")
