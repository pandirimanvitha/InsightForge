"""Semantic evidence retrieval compatible with the CMU research client."""

import json
from pathlib import Path

import numpy as np

from .models import SearchResult, SourceDocument


class SemanticResearchClient:
    """Embed documents once; rank searches by cosine similarity."""

    def __init__(self, data_path, embedder, min_similarity=None):

        # Load the same synthetic data used by Phase 1A.
        self.records = json.loads(
            Path(data_path).read_text(encoding="utf-8")
        )

        if not self.records:
            raise ValueError("Research collection is empty")

        # Create a lookup table so we can retrieve original documents.
        self.by_id = {
            record["id"]: record for record in self.records
        }

        if len(self.by_id) != len(self.records):
            raise ValueError("Duplicate source IDs found")

        self.embedder = embedder
        self.min_similarity = min_similarity

        # Each short research record is one chunk.
        passages = [
            record["title"] + ". " + record["text"]
            for record in self.records
        ]

        # Create document embeddings once, at initialization.
        vectors = np.asarray(
            embedder.encode(
                passages,
                normalize_embeddings=True
            ),
            dtype=np.float32
        )

        if vectors.ndim != 2 or len(vectors) != len(self.records):
            raise ValueError("Unexpected document embedding shape")

        self.document_vectors = self._normalized(vectors)

        # Useful for inspecting scores in our Colab notebook.
        self.last_scores = []

    @staticmethod
    def _normalized(vectors):
        """Normalize vectors so dot product equals cosine similarity."""

        norms = np.linalg.norm(
            vectors, axis=-1, keepdims=True
        )

        return vectors / np.maximum(norms, 1e-12)

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        """Return the most semantically similar research records."""

        self.last_scores = []

        if not query.strip() or limit <= 0:
            return []

        # Convert the research question into an embedding.
        query_vector = np.asarray(
            self.embedder.encode(
                [query],
                normalize_embeddings=True
            ),
            dtype=np.float32
        )

        if (
            query_vector.ndim != 2
            or query_vector.shape != (
                1, self.document_vectors.shape[1]
            )
        ):
            raise ValueError("Unexpected query embedding shape")

        query_vector = self._normalized(query_vector)[0]

        # Calculate similarity with all stored documents.
        similarities = self.document_vectors @ query_vector

        # Rank the highest scores first.
        order = np.argsort(-similarities, kind="stable")

        results = []

        for index in order:
            score = float(similarities[index])

            # Optional threshold for weakly matching evidence.
            if (
                self.min_similarity is not None
                and score < self.min_similarity
            ):
                continue

            record = self.records[index]

            self.last_scores.append({
                "id": record["id"],
                "score": round(score, 4)
            })

            results.append(
                SearchResult(
                    title=record["title"],
                    url=f"synthetic://{record['id']}",
                    snippet=record["text"][:180],
                    query=query
                )
            )

            if len(results) >= limit:
                break

        return results

    def fetch_source(
        self,
        result: SearchResult,
        max_chars: int = 12000
    ) -> SourceDocument:
        """Retrieve the original text for a selected result."""

        source_id = result.url.removeprefix("synthetic://")

        if (
            result.url != f"synthetic://{source_id}"
            or source_id not in self.by_id
        ):
            raise ValueError("Unknown synthetic source")

        record = self.by_id[source_id]

        return SourceDocument(
            title=record["title"],
            url=result.url,
            snippet=result.snippet,
            query=result.query,
            content=record["text"][:max_chars]
        )
