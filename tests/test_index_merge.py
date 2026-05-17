from datetime import date

from hf_paper_bot import merge_index_content
from hf_paper_bot import filter_relevant_papers
from hf_paper_bot import normalize_paper
from hf_paper_bot import NO_NEW_MARKER
from hf_paper_bot import build_email_message


def test_merge_keeps_recent_blocks():
    existing = (
        "---\nlayout: default\n---\n\n"
        "## 📅 2026-05-10\n\nold block\n"
        "## 📅 2026-04-01\n\nexpired block\n"
    )
    new_block = "2026-05-17\n\nnew block\n"
    merged = merge_index_content(existing, new_block, date(2026, 5, 17))
    assert "2026-05-17" in merged
    assert "2026-05-10" in merged
    assert "2026-04-01" not in merged


def test_merge_handles_empty_existing():
    merged = merge_index_content("", "2026-05-17\n\ncontent\n", date(2026, 5, 17))
    assert "2026-05-17" in merged


def test_filter_relevant_papers_strict_or(monkeypatch):
    monkeypatch.setenv("STRICT_OR_FILTER", "1")
    monkeypatch.delenv("OR_KEYWORDS", raising=False)
    monkeypatch.delenv("AI_KEYWORDS", raising=False)
    papers = [
        normalize_paper({"paper": {"id": "1", "title": "Route optimization", "summary": ""}}),
        normalize_paper({"paper": {"id": "2", "title": "Deep learning for vision", "summary": ""}}),
    ]
    filtered = filter_relevant_papers(papers)
    assert len(filtered) == 1
    assert filtered[0]["id"] == "1"


def test_merge_with_no_new_marker():
    new_block = f"2026-05-17\n\n{NO_NEW_MARKER}\n"
    merged = merge_index_content("", new_block, date(2026, 5, 17))
    assert "2026-05-17" in merged
    assert NO_NEW_MARKER in merged


def test_build_email_message():
    message = build_email_message(
        "subject",
        "content",
        "sender@example.com",
        ["to1@example.com", "to2@example.com"],
    )
    assert message["Subject"] == "subject"
    assert message["From"] == "sender@example.com"
    assert "to1@example.com" in message["To"]
