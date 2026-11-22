"""Offline tests for evidence-constrained dynamic ToT extension."""
import json
from dataclasses import replace
from types import SimpleNamespace

import pytest

from research_agent.decision_tot import WEIGHTS, evaluate, initial_candidates, render_tot
from research_agent.decision_tot_dynamic import (
    OfflineMitigationProposer, OpenRouterMitigationProposer,
    _parse_proposal, _source_registry, independently_evaluate_proposal,
    run_dynamic_tot, ProposalError,
)


@pytest.fixture
def sources():
    return [SimpleNamespace(url=f"synthetic://{sid}", content="Nonempty synthetic evidence for " + sid)
            for sid in ("SYN-001", "SYN-003", "SYN-004", "SYN-005", "SYN-006", "SYN-008")]


def test_offline_comparison_is_traceable_and_uses_beam(sources):
    result = run_dynamic_tot("Compare incident routing technologies", sources)
    assert result["mode"] == "offline_deterministic"
    assert result["model_calls"] == 0
    assert len(result["initial"]) == 3
    assert [b.candidate.option_id for b in result["beam"]] == ["A", "B"]
    assert len(result["refined"]) == 2
    assert all(x.candidate.depth == 2 for x in result["refined"])
    assert result["human_review_required"] is True
    assert "not observed" in result["note"]
    assert "Provisional" in render_tot(result)


def test_missing_policy_source_blocks_comparison(sources):
    missing = [s for s in sources if not s.url.endswith("SYN-008")]
    with pytest.raises(ProposalError, match="SYN-008"):
        run_dynamic_tot("Compare approaches", missing)


def test_missing_source_content_is_rejected(sources):
    sources[0].content = ""
    with pytest.raises(ProposalError, match="Missing evidence text"):
        run_dynamic_tot("Compare approaches", sources)


def test_mitigation_must_cite_its_source(sources):
    registry = _source_registry(sources)
    proposal = OfflineMitigationProposer().propose("q", initial_candidates()[1], registry)
    proposal["evidence_ids"] = ["SYN-005"]
    with pytest.raises(ProposalError, match="lack supporting"):
        _parse_proposal(proposal, "B", registry)


def test_model_cannot_raise_scores_directly(sources):
    class FakeProposer:
        mode = "fake"
        def propose(self, question, candidate, registry):
            p = OfflineMitigationProposer().propose(question, candidate, registry)
            p["ratings"] = {k: 5 for k in WEIGHTS}  # ignored by our independent scorer
            return p
    run = run_dynamic_tot("Compare approaches", sources, proposer=FakeProposer())
    assert run["refined"]
    assert max(x.score for x in run["refined"]) < 5


def test_hard_policy_block_overrides_any_bonus(sources):
    class MaliciousProposer:
        mode = "test_malicious"
        def propose(self, question, candidate, registry):
            proposal = OfflineMitigationProposer().propose(question, candidate, registry)
            proposal["controls"]["human_approval"] = False
            return proposal
    run = run_dynamic_tot("Compare approaches", sources, proposer=MaliciousProposer())
    assert run["best"] is None
    assert len(run["refined"]) == 2
    assert all(not r.eligible for r in run["refined"])
    assert all(t["status"] == "blocked_hard_policy" for t in run["proposal_trace"])


def test_unknown_mitigation_and_switched_option_rejected(sources):
    class InvalidProposer:
        mode = "test_invalid"
        def propose(self, question, candidate, registry):
            payload = OfflineMitigationProposer().propose(question, candidate, registry)
            payload["mitigations"] = ["unlimited_autonomous_routing"]
            return payload
    run = run_dynamic_tot("Compare approaches", sources, proposer=InvalidProposer())
    assert run["best"] is None
    assert all(t["status"] == "rejected_invalid_proposal" for t in run["proposal_trace"])
    assert run["stopped"] == "no_valid_refinement"


def test_provider_exception_does_not_leak_details(sources):
    class UnavailableProvider:
        def propose(self, *args):
            raise RuntimeError("SECRET_EXAMPLE_TOKEN")
    run = run_dynamic_tot("Compare approaches", sources, proposer=UnavailableProvider())
    assert run["best"] is None
    assert all(t["reason"] == "RuntimeError" for t in run["proposal_trace"])
    assert "SECRET_EXAMPLE_TOKEN" not in json.dumps(run["proposal_trace"])


def test_llm_proposer_uses_two_api_calls(sources):
    class FakeEndpoint:
        def __init__(self):
            self.chat = SimpleNamespace(completions=self)
            self.requests = []
        def create(self, **kwargs):
            self.requests.append(kwargs)
            query = json.loads(kwargs["messages"][1]["content"])
            option_id = query["option_id"]
            registry = _source_registry(sources)
            p = OfflineMitigationProposer().propose("q", initial_candidates()[0 if option_id == "A" else 1], registry)
            return SimpleNamespace(choices=[SimpleNamespace(
                finish_reason="stop", message=SimpleNamespace(content=json.dumps(p))
            )])
    fake = FakeEndpoint()
    proposer = OpenRouterMitigationProposer(fake, model="example-instruction-model")
    run = run_dynamic_tot("Compare approaches", sources, proposer=proposer)
    assert proposer.calls == 2
    assert len(fake.requests) == 2
    assert run["mode"] == "llm_proposed"
    assert len(run["refined"]) == 2
    assert all(t["status"] == "accepted" for t in run["proposal_trace"])


def test_truncated_llm_output_fails_safely(sources):
    class FakeEndpoint:
        def __init__(self):
            self.chat = SimpleNamespace(completions=self)
        def create(self, **kwargs):
            return SimpleNamespace(choices=[SimpleNamespace(
                finish_reason="length", message=SimpleNamespace(content='{"broken":')
            )])
    run = run_dynamic_tot(
        "Compare approaches", sources,
        proposer=OpenRouterMitigationProposer(FakeEndpoint(), "some-model")
    )
    assert run["best"] is None
    assert run["stopped"] == "no_valid_refinement"
    assert all(t["status"] == "rejected_invalid_proposal" for t in run["proposal_trace"])
