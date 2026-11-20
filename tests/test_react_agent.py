"""Offline tests for InsightForge's ReAct workflow."""

import json
from pathlib import Path

from research_agent.react_agent import ReActResearchAgent
from research_agent.research_tools import SyntheticResearchClient


DATA = (
    Path(__file__).resolve().parents[1]
    / "data/synthetic/research_notes.json"
)


class FakeDecider:
    """Return predefined model decisions for repeatable testing."""

    def __init__(self, actions):
        self.actions = iter(actions)

    def decide(self, question, queries, observations):
        return json.dumps(next(self.actions))


def test_search_then_finish_collects_sources():
    """Agent should search, observe evidence, then finish."""

    actions = [
        {
            "action": "search",
            "query": "high severity routing human approval"
        },
        {
            "action": "finish",
            "query": ""
        }
    ]

    agent = ReActResearchAgent(
        SyntheticResearchClient(DATA),
        FakeDecider(actions)
    )

    run = agent.run("Should we automate triage?")

    assert run.stop_reason == "finished"

    assert any(
        "SYN-001" in source.url
        for source in run.report.references
    )

    assert [step["action"] for step in run.trace] == [
        "search", "finish"
    ]


def test_invalid_action_is_rejected():
    """Unknown tools must never execute."""

    actions = [
        {"action": "execute_code", "query": "delete files"}
    ]

    agent = ReActResearchAgent(
        SyntheticResearchClient(DATA),
        FakeDecider(actions)
    )

    run = agent.run("Research incident triage")

    assert run.stop_reason == "invalid_action"
    assert run.report.references == []


def test_duplicate_query_is_skipped():
    """The agent should avoid repeating an identical search."""

    actions = [
        {"action": "search", "query": "human approval"},
        {"action": "search", "query": "human approval"},
        {"action": "finish", "query": ""}
    ]

    agent = ReActResearchAgent(
        SyntheticResearchClient(DATA),
        FakeDecider(actions)
    )

    run = agent.run("Research triage")

    assert "Duplicate" in run.trace[1]["observation"]
    assert len(run.report.references) >= 1


def test_step_limit_stops_unfinished_research():
    """The agent must respect its maximum step budget."""

    actions = [
        {"action": "search", "query": "human approval"}
    ]

    agent = ReActResearchAgent(
        SyntheticResearchClient(DATA),
        FakeDecider(actions),
        max_steps=1
    )

    run = agent.run("Research triage")

    assert run.stop_reason == "step_limit"
    assert len(run.trace) == 1


def test_no_evidence_is_reported():
    """Missing evidence must not become invented findings."""

    actions = [
        {
            "action": "search",
            "query": "volcanic magma seismology"
        },
        {"action": "finish", "query": ""}
    ]

    agent = ReActResearchAgent(
        SyntheticResearchClient(DATA),
        FakeDecider(actions)
    )

    run = agent.run("Unknown topic")

    assert run.report.references == []
    assert "Insufficient" in run.report.executive_summary[0]
