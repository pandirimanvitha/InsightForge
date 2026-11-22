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

- **A: 3.475/5** — Maintain auditable classification rules; add a correction path, fallback, and audit log
- **B: 3.200/5** — Retrieve runbooks and resolved ticket examples; validate retrieval freshness and add a low-confidence fallback

## Provisional outcome

**Provisional top-rated option:** Rule-based triage (3.475/5). This is not deployment approval.

**Limitations:** All scores are synthetic scenario judgments, not measured performance. The highest-rated option is a pilot hypothesis, not deployment approval.
**Source independence:** The input records are synthetic scenario viewpoints, not independent external evidence.
