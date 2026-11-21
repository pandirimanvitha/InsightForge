# InsightForge

AI Research Assistant for Product and Technology Decisions

## Overview
InsightForge is my CMU Agentic AI capstone project.

The goal is to build an autonomous research workflow that
gathers evidence, evaluates alternative solutions, and
produces recommendations for human review.

## Current Status
Phase 0: Initial project setup and course starter baseline.

## Technology
Python, Google Colab, GitHub.

## Starting Point
Adapted from the CMU Research Agent Starter Template.
Additional agent capabilities will be implemented and tested
during subsequent development phases.

## Running Baseline Tests

pip install -r requirements.txt
python -m pytest tests -q


## Development Progress

### Phase 0 - Project Setup
- Initialized project from CMU Research Agent Starter.
- Configured Google Colab and GitHub.
- Verified the original two tests.

### Phase 1A - Synthetic Evidence Retrieval
- Created eight synthetic incident-triage research records.
- Implemented keyword-based research retrieval.
- Integrated the new research tool with the CMU ResearchAgent.
- Added four automated tests.
- Verified six tests passing.

### Current Limitations
This version uses keyword-based retrieval rather than
semantic RAG. LLM-controlled ReAct reasoning, Tree-of-Thought,
multi-agent coordination, and advanced safety checks are
planned for subsequent development phases.


### Phase 1B — LLM-Driven ReAct Research

InsightForge now includes an OpenRouter-powered
ReAct-style research workflow.

Implemented capabilities:
- LLM-selected research actions (search or finish)
- Read-only synthetic evidence search
- Structured action validation
- Short-term observation history
- Maximum four-step research loop
- Duplicate query prevention
- Action and observation execution trace
- Source-backed extractive research reports
- Automated tests using simulated model decisions

The agent uses the existing CMU ResearchAgent
data structures and reuses the synthetic
research tool developed in Phase 1A.

#### Current Limitations

Retrieval is currently keyword-based rather than
semantic RAG. The final research brief uses extractive
summarization rather than LLM-generated comparative
recommendations.

Tree-of-Thought, four-agent coordination, and
additional evaluation guardrails will be implemented
in later phases.


### Phase 2 — Semantic Retrieval and Grounded RAG

InsightForge now supports embedding-based semantic retrieval
and evidence-grounded research brief generation.

#### Implemented Features

- Semantic retrieval using all-MiniLM-L6-v2 embeddings
- Cosine similarity search across synthetic research evidence
- Top-3 source retrieval with original source identifiers
- Integration with the existing ReAct research agent
- OpenRouter-based grounded brief generation
- Four-section research brief:
  Findings, Alternatives, Risks, and Missing Evidence
- Basic source citation validation
- Explicit handling of incomplete model responses
- Automated tests using simulated model responses

#### Demonstration

The research scenario compares three incident-triage approaches:
1. Rule-based classification
2. RAG-assisted classification
3. Agentic investigation with human oversight

The demonstration uses fictional evidence only.

The original ReAct run reached its step limit before retrieving
all required evidence. Additional human-directed semantic searches
were performed and recorded to complete evidence coverage.

The repository includes the original model output,
a human-reviewed example, and the execution trace.

#### Current Limitations

- Synthetic evidence rather than production data
- Small in-memory document collection
- Source citation validation does not guarantee claim accuracy
- Research completeness is not yet fully autonomous
- Free LLM providers may impose rate limits

Future phases will add Tree-of-Thought evaluation,
multi-agent coordination, stronger safety controls,
and quantitative evaluation.
