
"""Planner role for the InsightForge research workflow."""

from dataclasses import dataclass


@dataclass
class ResearchPlan:
    question: str
    subquestions: list[str]
    required_evidence: list[str]
    max_followups: int = 3


class PlannerAgent:

    def plan(self, question: str) -> ResearchPlan:

        if not isinstance(question, str) or not question.strip():
            raise ValueError("A research question is required")

        tasks = [
            "What incident classification alternatives exist?",
            "What are their benefits and limitations?",
            "What risks and mandatory policies apply?",
            "What evidence is missing before a decision?"
        ]

        required = [
            "SYN-001",  # Human approval
            "SYN-003",  # Operational risks
            "SYN-004",  # Rule-based option
            "SYN-005",  # RAG option
            "SYN-006",  # Agentic option
            "SYN-008"   # Data restrictions
        ]

        return ResearchPlan(
            question=question.strip(),
            subquestions=tasks,
            required_evidence=required,
            max_followups=3
        )
