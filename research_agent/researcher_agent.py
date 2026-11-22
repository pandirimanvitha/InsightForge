
"""Read-only research role using existing retrieval tools."""

import json
from pathlib import Path


class ResearcherAgent:

    def __init__(self, retrieval_client, dataset_path):
        self.client = retrieval_client

        records = json.loads(
            Path(dataset_path).read_text(encoding="utf-8")
        )

        self.catalog = {
            record["id"]: record
            for record in records
        }

        self.sources = {}
        self.trace = []

    def _accept(self, document, origin):
        source_id = document.url.removeprefix("synthetic://")
        reference = self.catalog.get(source_id)

        # Verify the result, not just its claimed source ID.
        if (
            reference is None
            or document.url != f"synthetic://{source_id}"
            or document.title != reference["title"]
            or document.content != reference["text"]
        ):
            raise ValueError(
                "Source is unknown or differs from approved evidence"
            )

        self.sources[source_id] = document

        self.trace.append({
            "action": "accept_source",
            "source_id": source_id,
            "origin": origin
        })

    def ingest(self, documents):
        """Load previously retrieved, verified evidence."""

        for document in documents:
            self._accept(document, "recorded_react_run")

    def recover(self, requested_ids, budget=3):
        """Search for missing sources within a strict budget."""

        if budget < 0:
            raise ValueError("Search budget cannot be negative")

        for source_id in list(
            dict.fromkeys(requested_ids)
        )[:budget]:

            if source_id in self.sources:
                continue

            if source_id not in self.catalog:
                raise ValueError("Unknown requested source ID")

            query = self.catalog[source_id]["title"]

            hits = self.client.search(
                query,
                limit=3
            )

            match = next(
                (
                    hit for hit in hits
                    if hit.url == f"synthetic://{source_id}"
                ),
                None
            )

            status = "not_found"

            if match is not None:
                document = self.client.fetch_source(match)

                self._accept(
                    document,
                    "targeted_semantic_search"
                )

                status = "verified_retrieved"

            self.trace.append({
                "action": "search",
                "query": query,
                "requested_id": source_id,
                "status": status
            })
