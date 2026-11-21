"""Tests for InsightForge's evidence-grounded report writer."""

from types import SimpleNamespace

import pytest

from research_agent.grounded_writer import GroundedBriefWriter
from research_agent.models import SourceDocument


class FakeOpenRouter:
    """Simulates OpenRouter without making API requests."""

    def __init__(self, answer):
        self.answer = answer
        self.calls = 0
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.calls += 1

        return SimpleNamespace(
            model="test-model",
            choices=[
                SimpleNamespace(
                    finish_reason="stop",
                    message=SimpleNamespace(
                        content=self.answer
                    )
                )
            ]
        )


SOURCE = SourceDocument(
    title="Human Approval Policy",
    url="synthetic://SYN-001",
    snippet="Human approval is required.",
    query="incident approval",
    content="P0/P1 incidents require human approval."
)


def test_no_evidence():
    """A report must not invent findings without sources."""

    client = FakeOpenRouter("Example response")
    writer = GroundedBriefWriter(client)

    result = writer.write_brief(
        "Should we automate routing?",
        []
    )

    assert "Insufficient" in result
    assert client.calls == 0


def test_valid_citation():
    """The model may cite a source that was retrieved."""

    client = FakeOpenRouter(
        "Human approval is required [SYN-001]."
    )

    writer = GroundedBriefWriter(client)

    result = writer.write_brief(
        "What approval is needed?",
        [SOURCE]
    )

    assert "[SYN-001]" in result


def test_fabricated_citation_rejected():
    """The model must not invent a source ID."""

    client = FakeOpenRouter(
        "A different policy exists [SYN-999]."
    )

    writer = GroundedBriefWriter(client)

    with pytest.raises(ValueError):
        writer.write_brief(
            "What approval is needed?",
            [SOURCE]
        )
