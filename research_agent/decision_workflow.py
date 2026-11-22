"""Connect Phase 2 ReAct evidence to bounded Phase 3 ToT decision review.

Only the read-only research client may recover missing sources. Recovery is
recorded as a separate controller action; it does not rewrite the ReAct trace.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .decision_tot import REQUIRED_SOURCES, render_tot
from .decision_tot_dynamic import run_dynamic_tot

# Include safety-risk evidence in addition to hard constraints and alternatives.
DECISION_EVIDENCE_IDS = REQUIRED_SOURCES | {"SYN-003"}


class CoverageError(ValueError):
    """The research-to-decision evidence gate could not be satisfied."""


@dataclass
class DecisionWorkflow:
    question: str
    original_stop_reason: str
    original_source_ids: list[str]
    recovered_sources: list[dict]
    final_source_ids: list[str]
    decision: dict

    def to_audit_dict(self) -> dict:
        """JSON-safe summary; don't serialize API clients or secrets."""
        def summary(evaluation):
            if evaluation is None:
                return None
            return {
                "option_id": evaluation.candidate.option_id,
                "name": evaluation.candidate.name,
                "score": evaluation.score,
                "eligible": evaluation.eligible,
                "blockers": evaluation.blockers,
                "evidence_ids": list(evaluation.candidate.evidence_ids),
                "safeguards": evaluation.candidate.plan,
            }

        result = self.decision
        return {
            "question": self.question,
            "original_stop_reason": self.original_stop_reason,
            "original_source_ids": self.original_source_ids,
            "controller_recovered_sources": self.recovered_sources,
            "final_source_ids": self.final_source_ids,
            "method": "3-branch, beam-2, depth-2 constrained refinement",
            "mode": result["mode"],
            "model_calls": result["model_calls"],
            "scoring_weights": result["weights"],
            "score_type": "provisional_synthetic_judgments",
            "baseline": summary(result["baseline"]),
            "beam": [summary(e) for e in result["beam"]],
            "refinements": [summary(e) for e in result["refined"]],
            "proposals": result["proposal_trace"],
            "provisional_best": summary(result["best"]),
            "human_review_required": result["human_review_required"],
            "limitations": result["note"],
        }

    def render(self) -> str:
        prefix = (
            "# InsightForge — Research-to-Decision Demonstration\n\n"
            f"**Original research stop:** {self.original_stop_reason}. "
            "Any missing evidence below was recovered by a separate "
            "read-only controller search, not by rewriting the original ReAct trace.\n\n"
            f"**Controller recovery count:** {len(self.recovered_sources)}\n\n"
            f"**Proposal mode:** {self.decision['mode']}\n\n"
        )
        return prefix + render_tot(self.decision)


def run_research_to_decision(
    question: str,
    research_run: Any,
    research_client: Any,
    dataset_path: str | Path,
    proposer: Any | None = None,
) -> DecisionWorkflow:
    """Check source authenticity, fill required gaps, then evaluate options."""
    if not question or not question.strip():
        raise CoverageError("A research question is required")
    if research_run.stop_reason not in {"finished", "step_limit"}:
        raise CoverageError(f"Unsafe research stop: {research_run.stop_reason}")

    records = json.loads(Path(dataset_path).read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in records}
    missing_from_dataset = DECISION_EVIDENCE_IDS - by_id.keys()
    if missing_from_dataset:
        raise CoverageError(f"Dataset missing required records: {sorted(missing_from_dataset)}")

    collected: dict[str, Any] = {}

    def validate(source: Any):
        url = getattr(source, "url", "")
        if not isinstance(url, str) or not url.startswith("synthetic://"):
            raise CoverageError("Non-synthetic source encountered")
        source_id = url[len("synthetic://"):]
        if source_id not in by_id:
            raise CoverageError(f"Source ID not in approved dataset: {source_id}")
        record = by_id[source_id]
        if getattr(source, "content", None) != record["text"]:
            raise CoverageError(f"Source content mismatch: {source_id}")
        return source_id

    for source in research_run.report.references:
        sid = validate(source)
        collected[sid] = source

    original_ids = sorted(collected)
    recovery = []
    for sid in sorted(DECISION_EVIDENCE_IDS - collected.keys()):
        record = by_id[sid]
        # Query a real read-only retrieval interface; never synthesize a hit.
        hits = research_client.search(record["title"], limit=3)
        selected = next((h for h in hits if h.url == f"synthetic://{sid}"), None)
        if selected is None:
            raise CoverageError(f"Required source {sid} not retrieved in top 3")
        source = research_client.fetch_source(selected)
        validate(source)
        collected[sid] = source
        recovery.append({
            "action": "controller_targeted_semantic_search",
            "query": record["title"],
            "source_id": sid,
            "reason": "Mandatory policy, risk, or option coverage gap",
        })

    still_missing = DECISION_EVIDENCE_IDS - collected.keys()
    if still_missing:
        raise CoverageError(f"Evidence incomplete: {sorted(still_missing)}")

    decision = run_dynamic_tot(
        question=question,
        sources=list(collected.values()),
        proposer=proposer,
        beam_width=2,
        max_depth=2,
        min_score=3.0,
    )
    return DecisionWorkflow(
        question=question,
        original_stop_reason=research_run.stop_reason,
        original_source_ids=original_ids,
        recovered_sources=recovery,
        final_source_ids=sorted(collected),
        decision=decision,
    )
