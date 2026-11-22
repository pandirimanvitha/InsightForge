
"""Four-role research workflow with bounded feedback."""

from .planner_agent import PlannerAgent
from .scope_guard import in_scope
from .researcher_agent import ResearcherAgent
from .critic_agent import CriticAgent
from .report_writer_agent import ReportWriterAgent


def run_four_roles(
    question,
    retrieval_client,
    dataset_path,
    initial_sources=(),
    proposer=None
):

    if not in_scope(question):
        status = "abstained_out_of_scope"

        return {
            "report": (
                "# InsightForge — Decision Withheld\n\n"
                "This question is outside the supported "
                "incident-triage research scope."
            ),
            "review": {
                "status": status,
                "missing": [],
                "decision": None
            },
            "audit": {
                "status": status,
                "roles": [],
                "original_source_ids": [],
                "requested_followups": [],
                "final_source_ids": [],
                "remaining_gaps": [],
                "search_actions": [],
                "proposal_mode": "not_run",
                "model_calls": 0,
                "provisional_best": None,
                "human_review_required": True,
                "stop_reason": "out_of_scope"
            }
        }

    # 1. PLANNER
    plan = PlannerAgent().plan(question)

    # 2. RESEARCHER
    researcher = ResearcherAgent(
        retrieval_client,
        dataset_path
    )

    researcher.ingest(initial_sources)

    original_ids = sorted(researcher.sources)

    # 3. CRITIC: Request missing evidence.
    critic = CriticAgent()

    requested = critic.gaps(
        plan,
        researcher.sources
    )

    # 4. RESEARCHER: One bounded follow-up round.
    researcher.recover(
        requested,
        budget=plan.max_followups
    )

    # 5. CRITIC: Review evidence and evaluate alternatives.
    review = critic.review(
        plan,
        researcher.sources,
        proposer=proposer
    )

    # 6. REPORT WRITER
    report = ReportWriterAgent().write(
        plan,
        review,
        researcher.sources
    )

    decision = review["decision"]

    best = (
        decision["best"]
        if decision is not None
        else None
    )

    # Save an inspectable audit record.
    audit = {
        "execution_mode": (
            "recorded_react_evidence_with_new_offline_evaluation"
        ),
        "roles": [
            "planner",
            "researcher",
            "critic_evaluator",
            "report_writer"
        ],
        "status": review["status"],
        "original_source_ids": original_ids,
        "requested_followups": requested,
        "final_source_ids": sorted(researcher.sources),
        "remaining_gaps": review["missing"],
        "search_actions": [
            action
            for action in researcher.trace
            if action["action"] == "search"
        ],
        "proposal_mode": (
            decision["mode"] if decision else "not_run"
        ),
        "model_calls": (
            decision["model_calls"] if decision else 0
        ),
        "provisional_best": (
            {
                "option": best.candidate.option_id,
                "score": best.score
            }
            if best else None
        ),
        "human_review_required": True
    }

    return {
        "report": report,
        "audit": audit,
        "review": review
    }
