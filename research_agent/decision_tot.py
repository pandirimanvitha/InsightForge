"""Transparent bounded Tree-of-Thought-style technology comparison.

Synthetic scorecards are provisional judgments, not measured outcomes.
"""
from dataclasses import dataclass, replace

WEIGHTS = {
    "evidence_quality": 0.30,
    "requirements_fit": 0.25,
    "feasibility": 0.20,
    "safety_operations": 0.15,
    "cost_complexity": 0.10,
}
REQUIRED_SOURCES = {"SYN-001", "SYN-008", "SYN-004", "SYN-005", "SYN-006"}
BASE_SCORES = {
    "A": (2.0, 4.0, 4.0, 4.0, 4.0),
    "B": (2.0, 4.0, 3.0, 3.0, 3.0),
    "C": (2.0, 4.0, 2.0, 2.0, 2.0),
}
OPTIONS = {
    "A": ("Rule-based triage", "SYN-004", "Maintain auditable classification rules"),
    "B": ("RAG-assisted triage", "SYN-005", "Retrieve runbooks and resolved ticket examples"),
    "C": ("Agentic investigation", "SYN-006", "Use read-only investigation tools to suggest routing"),
}


@dataclass(frozen=True)
class Candidate:
    option_id: str
    name: str
    depth: int
    plan: str
    evidence_ids: tuple[str, ...]
    ratings: dict[str, float]
    human_approval: bool = True
    read_only: bool = True
    approved_data: bool = True
    parent: str | None = None
    assumptions: tuple[str, ...] = ()


@dataclass
class Evaluation:
    candidate: Candidate
    score: float
    eligible: bool
    blockers: list[str]


def evaluate(candidate: Candidate) -> Evaluation:
    """Apply hard policies first; then a weighted 0-5 illustrative rubric."""
    if set(candidate.ratings) != set(WEIGHTS):
        raise ValueError("Candidate scores do not match the rubric")
    if any(not 0 <= score <= 5 for score in candidate.ratings.values()):
        raise ValueError("Each rubric rating must be between 0 and 5")
    blockers = []
    if not candidate.human_approval:
        blockers.append("P0/P1 routing requires human approval [SYN-001]")
    if not candidate.read_only:
        blockers.append("Research tools must be read-only [SYN-008]")
    if not candidate.approved_data:
        blockers.append("Only synthetic or approved public data [SYN-008]")
    score = round(sum(candidate.ratings[k] * w for k, w in WEIGHTS.items()), 3)
    return Evaluation(candidate, score, not blockers, blockers)


def initial_candidates() -> list[Candidate]:
    """Depth 1: three distinct, synthetic-evidence-backed options."""
    options = []
    for option_id, (name, source_id, plan) in OPTIONS.items():
        options.append(Candidate(
            option_id=option_id, name=name, depth=1, plan=plan,
            evidence_ids=("SYN-001", "SYN-008", source_id),
            ratings=dict(zip(WEIGHTS, BASE_SCORES[option_id])),
            assumptions=("Ratings are provisional scenario judgments, not measured results.",)
        ))
    return options


def refine(candidate: Candidate) -> Candidate:
    """Depth 2: propose one safeguard refinement per shortlisted option."""
    ratings = dict(candidate.ratings)
    if candidate.option_id == "A":
        plan = candidate.plan + "; add a correction path, fallback, and audit log"
        ratings["safety_operations"] = 4.5
    elif candidate.option_id == "B":
        plan = candidate.plan + "; validate retrieval freshness and add a low-confidence fallback"
        ratings["feasibility"] = 3.5
        ratings["safety_operations"] = 4.0
    else:
        plan = candidate.plan + "; enforce tool boundaries, approval, and latency budgets"
        ratings["safety_operations"] = 3.0
    return replace(
        candidate, depth=2, plan=plan, ratings=ratings,
        parent=candidate.option_id,
        assumptions=candidate.assumptions + (
            "Refinement benefits are hypotheses requiring pilot validation.",
        )
    )


def run_tot(question: str, sources: list, beam_width: int = 2,
            max_depth: int = 2, min_score: float = 3.0) -> dict:
    """Bounded breadth-3 -> beam-2 -> two-refinement comparison."""
    if not question.strip():
        raise ValueError("Research question must not be empty")
    if beam_width != 2 or max_depth != 2:
        raise ValueError("Capstone configuration requires beam_width=2, max_depth=2")
    if not 0 <= min_score <= 5:
        raise ValueError("min_score must be within 0..5")

    source_ids = {
        getattr(source, "url", "").removeprefix("synthetic://") for source in sources
    }
    missing = REQUIRED_SOURCES - source_ids
    if missing:
        raise ValueError(f"Missing required policy or option evidence: {sorted(missing)}")

    initial = [evaluate(c) for c in initial_candidates()]
    baseline = max((x for x in initial if x.eligible),
                   key=lambda item: (item.score, item.candidate.option_id),
                   default=None)
    # Hard-ineligible candidates are never selected, regardless of their score.
    allowed = [item for item in initial if item.eligible]
    beam = sorted(allowed, key=lambda item: (-item.score, item.candidate.option_id))[:beam_width]
    refined = [evaluate(refine(item.candidate)) for item in beam]
    finalists = [item for item in refined if item.eligible and item.score >= min_score]
    best = max(finalists, key=lambda item: (item.score, item.candidate.option_id)) if finalists else None
    return {
        "question": question,
        "weights": dict(WEIGHTS),
        "initial": initial,
        "baseline": baseline,
        "beam": beam,
        "refined": refined,
        "best": best,
        "stopped": "depth_limit",
        "source_ids": sorted(source_ids),
        "human_review_required": True,
        "note": ("All scores are synthetic scenario judgments, not measured performance. "
                 "The highest-rated option is a pilot hypothesis, not deployment approval."),
    }


def render_tot(result: dict) -> str:
    """Return an inspectable Markdown decision trace."""
    lines = ["# InsightForge — Provisional ToT Comparison", "",
             f"Question: {result['question']}", "",
             "**Method:** 3 initial branches; beam width 2; depth 2; one refinement per beam candidate.",
             "**Scoring:** " + ", ".join(f"{k}={v:.0%}" for k, v in result["weights"].items()),
             "", "## Initial branches", "",
             "| Option | Score / 5 | Hard constraints | Evidence |", "|---|---:|---|---|"]
    for evaluation in result["initial"]:
        c = evaluation.candidate
        lines.append(f"| {c.option_id}: {c.name} | {evaluation.score:.3f} | "
                     f"{'PASS' if evaluation.eligible else 'BLOCKED'} | {', '.join(c.evidence_ids)} |")
    baseline = result["baseline"]
    lines.extend(["", "## Single-stage baseline", "",
                  (f"{baseline.candidate.name}: {baseline.score:.3f}/5"
                   if baseline else "No compliant option."),
                  "", "## Beam selection", "",
                  ", ".join(item.candidate.option_id for item in result["beam"]),
                  "", "## Depth-2 refinements", ""])
    for evaluation in result["refined"]:
        c = evaluation.candidate
        lines.append(f"- **{c.option_id}: {evaluation.score:.3f}/5** — {c.plan}")
    lines.extend(["", "## Provisional outcome", ""])
    best = result["best"]
    if best is None:
        lines.append("No eligible candidate met the minimum score. Human review required.")
    else:
        lines.append(f"**Provisional top-rated option:** {best.candidate.name} "
                     f"({best.score:.3f}/5). This is not deployment approval.")
    lines.extend(["", "**Limitations:** " + result["note"],
                  "**Source independence:** The input records are synthetic "+
                  "scenario viewpoints, not independent external evidence.", ""])
    return "\n".join(lines)
