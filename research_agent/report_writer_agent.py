
"""Deterministic grounded report writer. No LLM request."""


class ReportWriterAgent:

    def write(self, plan, review, sources):

        # No recommendation if the Critic rejected the evidence.
        if review["status"] != "ready_for_human_review":

            missing = ", ".join(review["missing"])

            return (
                "# InsightForge — Decision Withheld\n\n"
                "Insufficient or unsafe evidence. "
                "Human review required. "
                f"Missing: {missing or 'policy / evaluation check'}.\n"
            )

        decision = review["decision"]
        best = decision["best"]

        def cite(source_id):
            return (
                f"{sources[source_id].content} "
                f"[{source_id}]"
            )

        return "\n".join([
            "# InsightForge — Synthetic Research Brief",
            "",
            "## Findings",
            "- " + cite("SYN-001"),
            "",
            "## Alternatives",
            "- **A: Rules:** " + cite("SYN-004"),
            "- **B: RAG:** " + cite("SYN-005"),
            "- **C: Agentic:** " + cite("SYN-006"),
            "",
            "## Risks",
            "- " + cite("SYN-003"),
            "- " + cite("SYN-008"),
            "",
            "## Provisional Decision",
            (
                f"- Top illustrative rubric score: "
                f"**{best.candidate.name}**, "
                f"**{best.score:.3f}/5**. "
                "Human review required; no routing changes."
            ),
            (
                "- All scenario scores and mitigation increases "
                "are assumptions, not observed accuracy "
                "or business benefits."
            ),
            "",
            "## Missing Evidence",
            (
                "- Actual accuracy, latency, cost and business "
                "impact were not measured in this synthetic "
                "collection. A controlled pilot is required."
            )
        ])
