"""Read-only search over InsightForge's synthetic research notes."""

import json
import re
from pathlib import Path

from .models import SearchResult, SourceDocument


# Ignore common words when comparing research questions.
STOPWORDS = {
    "a", "an", "and", "are", "be", "can", "do", "for", "in",
    "is", "of", "on", "or", "our", "should", "the", "to",
    "we", "what", "with", "would"
}


def keywords(text: str) -> set[str]:
    """Extract useful lowercase words from text."""

    words = re.findall(r"[a-z0-9]+", text.lower())

    return {
        word for word in words
        if word not in STOPWORDS
    }


class SyntheticResearchClient:
    """Search synthetic evidence using the CMU web-client interface."""

    def __init__(self, data_path: str | Path):

        # Load the synthetic research collection.
        self.records = json.loads(
            Path(data_path).read_text(encoding="utf-8")
        )

        # Index documents by ID for retrieval.
        self.by_id = {
            record["id"]: record
            for record in self.records
        }

    def search(
        self,
        query: str,
        limit: int = 5
    ) -> list[SearchResult]:
        """Rank matching documents without accessing the internet."""

        query_words = keywords(query)

        # Handle empty questions or invalid limits.
        if not query_words or limit <= 0:
            return []

        ranked = []

        for record in self.records:

            title_words = keywords(record["title"])
            body_words = keywords(record["text"])

            # Matching title words count twice.
            score = 2 * len(query_words & title_words)
            score += len(query_words & body_words)

            if score > 0:
                ranked.append((score, record))

        # Rank by score, then use ID for reproducible ties.
        ranked.sort(
            key=lambda item: (-item[0], item[1]["id"])
        )

        # Convert matching records into CMU SearchResult objects.
        return [
            SearchResult(
                title=record["title"],
                url=f"synthetic://{record['id']}",
                snippet=record["text"][:180],
                query=query,
            )
            for _, record in ranked[:limit]
        ]

    def fetch_source(
        self,
        result: SearchResult,
        max_chars: int = 12000
    ) -> SourceDocument:
        """Retrieve a synthetic document by source ID."""

        source_id = result.url.removeprefix("synthetic://")
        record = self.by_id[source_id]

        return SourceDocument(
            title=record["title"],
            url=result.url,
            snippet=result.snippet,
            query=result.query,
            content=record["text"][:max_chars],
        )
