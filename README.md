# InsightForge
### AI Research Assistant for Product and Technology Decisions

**Carnegie Mellon University — Agentic AI Capstone Project**

## 1. Project Overview

InsightForge is an AI-assisted research prototype designed to gather evidence, compare technology alternatives, identify risks, and produce grounded recommendations for human review.

The capstone investigates the research question:

**Should a hypothetical fintech organization adopt AI-assisted incident classification and routing?**

Three approaches are evaluated:

- **Option A:** Rule-based incident classification
- **Option B:** Retrieval-Augmented Generation (RAG)-assisted classification
- **Option C:** Agentic incident investigation with human oversight

The project uses eight synthetic research records. No real company incidents, customer records, or production systems are involved.

## 2. System Architecture

InsightForge combines several agentic AI concepts:

**ReAct Research**

A bounded research loop allows an LLM to select read-only search or finish actions. Actions are validated and logged. The recorded example reached its step limit, after which additional evidence recovery was performed.

**Retrieval-Augmented Generation**

Semantic retrieval uses `sentence-transformers/all-MiniLM-L6-v2` embeddings and cosine similarity to locate relevant synthetic evidence. A keyword-based retrieval implementation provides a comparison baseline.

**Tree-of-Thought Evaluation**

Three predefined alternatives are evaluated using weighted criteria. A beam-search-style process retains two promising options for further refinement.

Mitigation proposals are independently validated against source evidence and mandatory safety policies. Numerical scores are illustrative, not measured business performance.

**Four-Agent Workflow**

1. **Planner Agent:** Defines research tasks and required evidence.
2. **Researcher Agent:** Retrieves and verifies source documents.
3. **Critic / Evaluator Agent:** Identifies evidence gaps, evaluates alternatives, and enforces constraints.
4. **Report Writer Agent:** Produces a grounded research brief for human review.

The Critic can request up to three additional read-only evidence searches.

The integrated offline workflow uses deterministic agent roles. Separate components support optional LLM-driven ReAct actions, grounded writing, and mitigation proposals.

## 3. Safety and Reliability

The prototype includes:

- Human approval requirements for high-severity incident recommendations
- Read-only research operations
- Synthetic or otherwise approved data restrictions
- Source integrity and citation checks
- Bounded research steps and follow-up searches
- Rejection of altered evidence
- Abstention when mandatory evidence is unavailable
- Conservative rejection of out-of-scope questions
- Explicit uncertainty and human-review requirements

**InsightForge does not change incident routing or execute production actions.**

## 4. Evaluation Results

The system was evaluated using ten controlled synthetic scenarios and eight retrieval benchmark questions.

| Metric | Observed result |
|---|---|
| Scenarios passing before scope validation | 9/10 |
| Scenarios passing after scope validation | 10/10 |
| Automated regression tests | 41 passed |
| Initial required-evidence coverage | 64.6% |
| Full-workflow required-evidence coverage | 87.5% |
| Evidence coverage improvement | +22.9 percentage points |
| Additional searches across evaluation | 13 |
| Median offline scenario runtime | 18.535 ms |

### Keyword vs. Semantic Retrieval

| Metric | Keyword Search | Semantic Retrieval |
|---|---|---|
| Top-1 accuracy | 87.5% | 87.5% |
| Top-3 recall | 100% | 100% |
| Mean reciprocal rank | 0.938 | 0.938 |

Both retrieval approaches achieved identical aggregate scores on the eight-question benchmark, although their ranking errors differed.

These measurements demonstrate prototype behavior on a small synthetic dataset. They do not establish production-level classification accuracy, real-world financial benefits, or superior performance of semantic retrieval.

The median runtime reflects the offline evaluation, not end-to-end latency for a live LLM workflow.

## 5. Technology Stack

- Python
- Google Colab
- GitHub
- NumPy
- Sentence Transformers
- OpenRouter for optional LLM interactions
- Pytest for automated testing

## 6. Repository Structure

- `research_agent/` — Research clients, ReAct agent, semantic retrieval, ToT evaluation, four-agent workflow, and safety checks
- `data/synthetic/` — Synthetic research evidence
- `tests/` — Automated regression tests
- `evaluation/` — Scenario evaluation and retrieval benchmark results
- `examples/` — Research briefs, decision summaries, and execution traces
- `notebooks/` — Google Colab development notebook
- `requirements.txt` — Python dependencies

## 7. Running the Project

Clone or download the repository and install its dependencies:

`pip install -r requirements.txt`

Run the offline automated tests:

`python -m pytest tests -q`

For the interactive research demonstrations, open `notebooks/InsightForge_Capstone.ipynb` in Google Colab.

The notebook contains the development workflow, saved research replay, four-agent demonstration, safety tests, and evaluation steps. Some notebook cells use a Google Drive project path and must be adjusted for another environment.

Offline tests do not require an OpenRouter API key. Optional live model calls require a separately configured API key and may be affected by provider availability and rate limits.

## 8. Key Findings

The prototype demonstrated that:

- A Critic-guided recovery step can improve required-evidence coverage.
- Independent policy validation can prevent unsupported recommendations.
- Out-of-scope questions can be rejected before research begins.
- Four coordinated roles can produce a traceable research-to-decision workflow.
- More complex retrieval methods do not necessarily outperform simpler baselines on a small dataset.

The illustrative ToT comparison provisionally ranked rule-based triage highest, with a refined score of 3.487/5. This is a hypothetical rubric result and not a measured superiority claim.

## 9. Limitations and Future Work

The research collection contains only eight synthetic documents. The system has not been tested with real incident streams, measured business outcomes, or independently verified industry research.

The Planner and scope guard are specific to incident-triage research. The integrated offline workflow is deterministic rather than a fully autonomous multi-agent system.

Future improvements include larger authorized datasets, independent claim verification, broader scope validation, human usability testing, measured LLM latency, and controlled pilot studies.

## 10. Acknowledgments and Development Transparency

This project was adapted from the **CMU Research Agent Starter Template** and extended through iterative experimentation with retrieval, reasoning, agent coordination, and evaluation techniques.

Generative AI assistance, including ChatGPT, was used in drafting and debugging substantial portions of the implementation and documentation. The resulting workflows were run, inspected, debugged, and evaluated in Google Colab. Final interpretations and representations of results require human review.

This is an educational research prototype, not a production incident-management system.
