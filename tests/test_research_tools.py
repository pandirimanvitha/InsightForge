"""Tests for InsightForge's synthetic research tool."""

from pathlib import Path

from research_agent.agent import ResearchAgent, ResearchConfig
from research_agent.research_tools import SyntheticResearchClient


# Locate our synthetic dataset relative to this test file.
DATA = (
    Path(__file__).resolve().parents[1]
    / "data/synthetic/research_notes.json"
)


class OfflineWriter:
    """Prevent LLM API calls during automated tests."""

    def write_report(self, topic, sources):
        return ""


def test_human_approval_policy_is_found():
    """The tool should retrieve the required policy."""

    client = SyntheticResearchClient(DATA)

    results = client.search(
        "high severity incident routing human approval"
    )

    assert results
    assert results[0].url == "synthetic://SYN-001"


def test_unrelated_question_has_no_results():
    """The tool must not invent evidence for unrelated topics."""

    client = SyntheticResearchClient(DATA)

    results = client.search(
        "volcanic magma seismology"
    )

    assert results == []


def test_search_respects_result_limit():
    """The tool should honor the requested maximum."""

    client = SyntheticResearchClient(DATA)

    results = client.search(
        "incident routing",
        limit=2
    )

    assert len(results) <= 2


def test_existing_agent_can_use_synthetic_tool():
    """The CMU agent should work with our research client."""

    agent = ResearchAgent(
        ResearchConfig(
            max_queries=2,
            max_sources=3
        )
    )

    agent.web = SyntheticResearchClient(DATA)
    agent.llm_writer = OfflineWriter()

    report = agent.research(
        "high severity incident routing human approval"
    )

    # The report must contain references.
    assert report.references

    # At least one source must mention human approval.
    assert any(
        "human approval" in source.content.lower()
        for source in report.references
    )
