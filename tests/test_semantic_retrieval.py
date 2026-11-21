"""Offline tests for InsightForge's semantic retriever."""

import json

import numpy as np

from research_agent.semantic_retrieval import (
    SemanticResearchClient
)


class FakeEmbedder:
    """Return predictable vectors for testing."""

    def encode(self, texts, normalize_embeddings=True):
        vectors = []

        for text in texts:
            text = text.lower()

            if (
                "approve" in text
                or "sign off" in text
                or "approval" in text
            ):
                vectors.append([1.0, 0.0, 0.0])

            elif "routing" in text or "assign" in text:
                vectors.append([0.0, 1.0, 0.0])

            else:
                vectors.append([0.0, 0.0, 1.0])

        return np.array(vectors, dtype=np.float32)


def make_client(tmp_path, min_similarity=None):
    """Create a small temporary research dataset."""

    data = [
        {
            "id": "SYN-A",
            "title": "Approval policy",
            "text": "Human approval is required for critical incidents."
        },
        {
            "id": "SYN-B",
            "title": "Routing",
            "text": "Routing tickets to responders."
        },
        {
            "id": "SYN-C",
            "title": "Cafeteria",
            "text": "Today's lunch menu."
        }
    ]

    path = tmp_path / "notes.json"

    path.write_text(
        json.dumps(data),
        encoding="utf-8"
    )

    return SemanticResearchClient(
        path,
        FakeEmbedder(),
        min_similarity=min_similarity
    )


def test_semantic_search_finds_paraphrased_policy(tmp_path):
    """Paraphrased approval questions should find the policy."""

    client = make_client(tmp_path)

    results = client.search(
        "Who needs to sign off?",
        limit=1
    )

    assert len(results) == 1
    assert results[0].url == "synthetic://SYN-A"


def test_fetch_source_returns_original_text(tmp_path):
    """The retrieved reference must point to original evidence."""

    client = make_client(tmp_path)

    result = client.search("sign off", limit=1)[0]
    document = client.fetch_source(result)

    assert "Human approval" in document.content
    assert document.url == result.url


def test_empty_question_and_result_limit(tmp_path):
    """Blank questions and result limits should be respected."""

    client = make_client(tmp_path)

    assert client.search("", limit=3) == []
    assert client.search("sign off", limit=0) == []

    results = client.search("routing", limit=2)

    assert len(results) == 2


def test_similarity_threshold_filters_results(tmp_path):
    """A threshold can filter unrelated vectors."""

    client = make_client(
        tmp_path,
        min_similarity=0.5
    )

    results = client.search("sign off", limit=3)

    assert len(results) == 1
