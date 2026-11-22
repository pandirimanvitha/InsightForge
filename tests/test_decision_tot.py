from types import SimpleNamespace
from dataclasses import replace
import pytest
from research_agent.decision_tot import (
    WEIGHTS, Candidate, evaluate, initial_candidates, run_tot, render_tot,
)

SOURCES = [SimpleNamespace(url=f"synthetic://{x}") for x in
           ("SYN-001","SYN-003","SYN-004","SYN-005","SYN-006","SYN-008")]

def test_three_initial_two_beam_two_refinements():
    run = run_tot("Compare incident triage designs", SOURCES)
    assert len(run["initial"]) == 3
    assert len(run["beam"]) == 2
    assert len(run["refined"]) == 2
    assert {x.candidate.option_id for x in run["beam"]} == {"A", "B"}
    assert all(x.candidate.depth == 2 for x in run["refined"])
    assert run["stopped"] == "depth_limit"

def test_weighted_scoring_is_reproducible():
    assert sum(WEIGHTS.values()) == pytest.approx(1.0)
    score = evaluate(initial_candidates()[0]).score
    assert score == pytest.approx(3.4)

def test_hard_constraint_overrides_perfect_score():
    candidate = replace(initial_candidates()[0], human_approval=False,
                        ratings={k:5 for k in WEIGHTS})
    evaluation = evaluate(candidate)
    assert evaluation.score == 5
    assert not evaluation.eligible
    assert 'human approval' in evaluation.blockers[0]

def test_both_policy_controls_required():
    without_privacy = [s for s in SOURCES if not s.url.endswith("SYN-008")]
    with pytest.raises(ValueError, match="SYN-008"):
        run_tot("Compare approaches", without_privacy)

def test_missing_option_evidence_stops_decision():
    without_rag = [s for s in SOURCES if not s.url.endswith("SYN-005")]
    with pytest.raises(ValueError, match="SYN-005"):
        run_tot("Compare approaches", without_rag)

def test_result_is_provisional_and_traceable():
    run = run_tot("Compare approaches", SOURCES)
    assert run["human_review_required"]
    assert run["best"] is not None
    text = render_tot(run)
    assert "initial branches" in text.lower()
    assert "refinements" in text.lower()
    assert "not deployment approval" in text
