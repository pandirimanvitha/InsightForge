# InsightForge — Research-to-Decision Demonstration

**Original research stop:** step_limit. Any missing evidence below was recovered by a separate read-only controller search, not by rewriting the original ReAct trace.

**Controller recovery count:** 2

**Proposal mode:** offline_deterministic

# InsightForge — Provisional ToT Comparison

Question: Should a hypothetical fintech company adopt AI-powered incident classification and routing? Research benefits, alternatives, risks, and human approval requirements.

**Method:** 3 initial branches; beam width 2; depth 2; one refinement per beam candidate.
**Scoring:** evidence_quality=30%, requirements_fit=25%, feasibility=20%, safety_operations=15%, cost_complexity=10%

## Initial branches

| Option | Score / 5 | Hard constraints | Evidence |
|---|---:|---|---|
| A: Rule-based triage | 3.400 | PASS | SYN-001, SYN-008, SYN-004 |
| B: RAG-assisted triage | 2.950 | PASS | SYN-001, SYN-008, SYN-005 |
| C: Agentic investigation | 2.500 | PASS | SYN-001, SYN-008, SYN-006 |

## Single-stage baseline

Rule-based triage: 3.400/5

## Beam selection

A, B

## Depth-2 refinements

- **A: 3.487/5** — Maintain auditable classification rules; proposed pilot safeguards: retain a manual fallback; schedule rule and ownership reviews
- **B: 3.025/5** — Retrieve runbooks and resolved ticket examples; proposed pilot safeguards: verify retrieved runbook freshness; flag low-confidence suggestions

## Provisional outcome

**Provisional top-rated option:** Rule-based triage (3.487/5). This is not deployment approval.

**Limitations:** Ratings and mitigation score increments are illustrative scenario judgments, not observed business performance. All input sources are synthetic, not independent external studies. A human must approve any pilot decision.
**Source independence:** The input records are synthetic scenario viewpoints, not independent external evidence.
