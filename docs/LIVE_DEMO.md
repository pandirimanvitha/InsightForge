# InsightForge: Live AI Product Research Demo

## Purpose
This optional live dashboard extends the original synthetic incident-triage case study to general AI product and technology research. Each new research run conducts fresh public-web searches and new LLM calls. It does not replay saved synthetic research outputs.

Main entrypoint: `demo_ui_strategy_langchain_rag_report_fixed.py`.

## Architecture and course concepts
- **Planner:** asks an LLM to propose three question-specific options and three search queries.
- **Researcher:** runs Tavily public web searches; a bounded ReAct-style model decision may request one further search or finish.
- **Temporary retrieval memory:** TF-IDF sparse-vector retrieval indexes web excerpts gathered in the current run (not persistent or neural embedding storage).
- **Critic/Evaluator:** checks evidence sufficiency and domain diversity and retrieves evidence for each alternative. Domain diversity does not prove independent or opposing perspectives.
- **Tree of Thought:** scores three alternatives using weighted criteria, keeps the top two, and requests evidence-linked mitigation proposals.
- **Report Writer:** drafts a cited decision brief. Invalid formatting or citations can trigger one correction; unresolved validation errors fail closed.
- **Explain Decision:** makes a fresh LLM call using the prior run's temporary evidence, without a new web search.
- **LangSmith:** traces model and instrumented tool operations when enabled.

Roles are specialized and **sequential**; this is not parallel multi-agent execution. The ReAct action is bounded, not an indefinite multi-step autonomous loop in the live application. The earlier offline case study also contains a separate bounded multi-step ReAct agent.

## Setup
1. Clone the repository and install: `pip install -r requirements_live.txt`.
2. Supply `OPENROUTER_API_KEY`, `TAVILY_API_KEY`, and `INSIGHTFORGE_DEMO_PASSWORD` via environment variables or Google Colab Secrets. **Never commit their values.**
3. Set `OPENROUTER_MODEL=google/gemini-2.5-flash-lite` for the primary paid model used in observed runs; optional `OPENROUTER_FALLBACK_MODEL=openai/gpt-4.1-mini`.
4. Optional LangSmith tracing: set `LANGSMITH_API_KEY`, `LANGSMITH_TRACING=true`, `LANGSMITH_AGENT_ID=insightforge-cmu`, and `LANGSMITH_AGENT_ENVIRONMENT=local`; make sure the agent exists in your LangSmith workspace.
5. Run: `python demo_ui_strategy_langchain_rag_report_fixed.py`.
6. Open the Gradio URL; login name is `reviewer` and the password is the `INSIGHTFORGE_DEMO_PASSWORD` value. Each completed research run has a new audit, report and evidence memory. The Explain tab requires a successful preceding run in that browser session.

## Observed live results (November 22, 2026)

| Scenario | Status | Retrieved sources | Model calls | Elapsed | Provisional top-ranked alternative |
|---|---|---:|---:|---:|---|
| AI feature prioritization for B2B SaaS | `ready_for_human_review` | 12 | 5 | 17.92 s | AI onboarding assistant (3.95/5) |
| Financial-services AI assistant: build vs buy vs hybrid | `ready_for_human_review` | 10 | 6 | 13.13 s | Purchase existing platform (3.80/5) |

The machine-readable audits are in `evaluation/live_web/`. Each shows `loaded_saved_results=false`; both runs were served by Gemini 2.5 Flash-Lite. The build-vs-buy report required one citation-format correction (`report_writer_repairs=1`). The Explain feature was subsequently demonstrated for both use cases, but its output is not included in these audit JSON records.

These two successful runs are **observational demonstrations, not a statistical performance benchmark**. Their scores are subjective model judgments, not measured business outcomes or validated ROI.

## Safety, evaluation boundaries and limitations
- Research tools are read-only; no production systems, customer data or employer repositories are accessed.
- Citations are checked for syntax and known source identifiers. **This does not verify that every cited source supports every claim**, nor that search excerpts are current, independent or unbiased.
- Web sources may be vendor-authored, promotional, outdated, incomplete or misleading.
- The minimum number of sources/domains is a basic adequacy check, not a calibrated confidence score or human-validated groundedness percentage.
- Research operations, LLM calls and correction attempts are bounded. A live error is reported, not replaced with a previously stored answer.
- Recommendations remain provisional; human review is required before business or operational decisions.
- LangSmith traces may capture prompts, model outputs and web excerpts. Use public examples only and check sharing settings.

## Separate original controlled evaluation
The initial synthetic incident-triage baseline, its 41 automated tests, ten controlled scenarios, and its keyword-vs-semantic retrieval comparison remain unchanged. **Do not combine those offline metrics with live-web performance claims.**

## Academic transparency
Adapted from a CMU Research Agent starter template and developed with substantial generative AI support for code, debugging, reports and presentation preparation. All work should be reviewed and disclosed in accordance with course policy.