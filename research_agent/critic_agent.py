
"""Independent evidence gate and ToT evaluation role."""

from .decision_tot_dynamic import run_dynamic_tot


class CriticAgent:

    def gaps(self, plan, sources):
        """Identify which required evidence records are missing."""

        return sorted(
            set(plan.required_evidence) - set(sources)
        )

    def review(self, plan, sources, proposer=None):

        missing = self.gaps(plan, sources)

        # Never make a comparison with incomplete required evidence.
        if missing:
            return {
                "status": "abstained_missing_evidence",
                "missing": missing,
                "decision": None
            }

        # Reuse our existing, independently scored ToT evaluator.
        decision = run_dynamic_tot(
            question=plan.question,
            sources=list(sources.values()),
            proposer=proposer,
            beam_width=2,
            max_depth=2
        )

        best = decision["best"]

        # Weighted scores cannot override safety requirements.
        if (
            best is None
            or not best.eligible
            or not all([
                best.candidate.human_approval,
                best.candidate.read_only,
                best.candidate.approved_data
            ])
        ):
            return {
                "status": "abstained_unsafe_or_incomplete",
                "missing": [],
                "decision": decision
            }

        return {
            "status": "ready_for_human_review",
            "missing": [],
            "decision": decision
        }
