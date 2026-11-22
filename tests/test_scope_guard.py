
"""Regression tests for InsightForge's scope guard."""

from pathlib import Path

from research_agent.scope_guard import in_scope
from research_agent.four_role_workflow import run_four_roles


DATA = (
    Path(__file__).resolve().parents[1]
    / "data/synthetic/research_notes.json"
)


def test_valid_incident_question():
    assert in_scope(
        "Should we use AI for incident classification and routing?"
    )


def test_unrelated_question_rejected():
    assert not in_scope("What is the weather on Mars?")
    assert not in_scope("How do I prepare dinner?")


def test_out_of_scope_never_calls_retrieval():

    class ForbiddenRetriever:

        def search(self, query, limit=3):
            raise AssertionError("Search should not be called")

        def fetch_source(self, result):
            raise AssertionError("Fetch should not be called")

    result = run_four_roles(
        question="What is the weather on Mars?",
        retrieval_client=ForbiddenRetriever(),
        dataset_path=DATA,
        initial_sources=[]
    )

    assert (
        result["audit"]["status"]
        == "abstained_out_of_scope"
    )

    assert result["audit"]["provisional_best"] is None
    assert result["audit"]["search_actions"] == []
    assert result["audit"]["model_calls"] == 0
