
"""Conservative scope check for InsightForge's demonstration."""

import re


def in_scope(question):
    if not isinstance(question, str):
        return False

    text = question.strip().lower()

    if not text or len(text) > 1000:
        return False

    # This prototype researches incident-triage decisions only.
    incident_context = re.search(
        r"\bincidents?\b",
        text
    )

    decision_context = re.search(
        r"\b(triage|routing|classification|categorization)\b",
        text
    )

    return bool(incident_context and decision_context)
