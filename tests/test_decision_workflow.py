"""Integration tests: Phase 2 evidence -> Phase 3 bounded decision."""
import json
from types import SimpleNamespace

import pytest

from research_agent.decision_workflow import (
    CoverageError, run_research_to_decision,
)


@pytest.fixture
def setup_case(tmp_path):
    ids = ("SYN-001", "SYN-003", "SYN-004", "SYN-005", "SYN-006", "SYN-008")
    dataset = [{"id": sid, "title": "Evidence title " + sid,
                "text": "Original evidence content " + sid} for sid in ids]
    path = tmp_path / "research_notes.json"
    path.write_text(json.dumps(dataset), encoding="utf-8")
    by_id = {r["id"]: r for r in dataset}

    def doc(sid):
        return SimpleNamespace(
            url=f"synthetic://{sid}", content=by_id[sid]["text"], title=by_id[sid]["title"]
        )

    class Client:
        def __init__(self):
            self.queries = []
        def search(self, query, limit=3):
            self.queries.append(query)
            sid = query.split()[-1]
            return [SimpleNamespace(url=f"synthetic://{sid}")]
        def fetch_source(self, hit):
            return doc(hit.url[len("synthetic://"):])

    run = SimpleNamespace(
        stop_reason="step_limit",
        report=SimpleNamespace(references=[doc(sid) for sid in ("SYN-001","SYN-003","SYN-004","SYN-006")]),
    )
    return path, Client(), run, doc


def test_controller_recovers_two_missing_sources_without_rewriting_history(setup_case):
    path, client, run, doc = setup_case
    original_ref_count = len(run.report.references)
    result = run_research_to_decision("Compare options", run, client, path)
    assert run.stop_reason == "step_limit"
    assert len(run.report.references) == original_ref_count
    assert {e["source_id"] for e in result.recovered_sources} == {"SYN-005", "SYN-008"}
    assert result.decision["best"] is not None
    assert result.decision["human_review_required"]
    assert result.to_audit_dict()["controller_recovered_sources"] == result.recovered_sources
    assert "not by rewriting" in result.render()


def test_rejects_tampered_evidence(setup_case):
    path, client, run, doc = setup_case
    run.report.references[0].content = "Invented source content"
    with pytest.raises(CoverageError, match="content mismatch"):
        run_research_to_decision("Compare options", run, client, path)


def test_rejects_unavailable_required_source(setup_case):
    path, client, run, doc = setup_case
    client.search = lambda query, limit=3: []
    with pytest.raises(CoverageError, match="not retrieved"):
        run_research_to_decision("Compare options", run, client, path)


def test_does_not_search_when_all_evidence_present(setup_case):
    path, client, run, doc = setup_case
    run.report.references.extend([doc("SYN-005"), doc("SYN-008")])
    result = run_research_to_decision("Compare options", run, client, path)
    assert client.queries == []
    assert result.recovered_sources == []
    assert result.decision["best"] is not None
