# InsightForge — Final Capstone Build Checklist

**Prepared:** 19 November 2026  
**Course deadline (confirmed by learner):** Monday, 23 November 2026 at **9:29 AM MST (America/Denver)**. Aim to submit the prior evening rather than close to the cutoff.  
**Working assumption:** 2 build days on Sat 21 and Sun 22 Nov, up to 16 hours available each; Thu/Fri used for setup.  
**Course track:** Research Assistant  
**Scenario:** A wholly synthetic organization's AI-powered production-incident triage decision. Never upload employer/customer data or secrets.

## Working agreement

- Maintain **one** InsightForge codebase and one main `InsightForge_Capstone.ipynb` notebook. Keep past checkpoints as design history; do not fabricate dated code commits.
- Work on a small runnable increment, **test it**, inspect the output, then save a commit. If the acceptance test fails, **stop and debug** before adding a feature.
- Use the supplied **CMU Research Agent starter** as an attributed starting point. Do not claim its initial code is your own.
- Treat `offline_demo` as a deterministic fallback for tests, not as proof of autonomous LLM behavior. Record at least one real model-driven tool-selection trace if possible.
- Maintain a `docs/BUILD_LOG.md` with actual dates, commands, results, errors, fixes and decisions.

## Phase 0 — THU/FRI: accounts, course starter and first working tests

- [x] **0.1** Confirm the exact Canvas due **time and time zone**: Monday, 23 November 2026 at **9:29 AM MST** (as provided from Canvas).
- [ ] **0.2** Create or reopen `insightforge` in GitLab; make it **private** for development. Initialize with a README (if new).
- [ ] **0.3** Create a Drive folder `InsightForge_CMU` and a Colab notebook `InsightForge_Capstone.ipynb` in that folder.
- [ ] **0.4** Upload **only** `CMU_research_agent_starter.zip` (12 KB), not the entire 163 MB course archive; extract into Drive's `InsightForge_CMU/insightforge` folder. Do not re-extract over edited files.
- [ ] **0.5** Install starter requirements and execute `python -m pytest tests -q`.
- [ ] **0.6** Confirm the result is **2 passed** (locally verified with starter; investigate any Colab differences).
- [ ] **0.7** Add a clear notebook Markdown cell explaining the project goal, selected CMU starter, and that the first run is a baseline.
- [ ] **0.8** Save first source snapshot in GitLab via Web IDE; commit with actual date, e.g. `Initialize InsightForge from CMU research-agent starter`.

**STOP GATE A:** Can the starter's two tests pass in Colab, and can you see `README.md`, `research_agent/`, `tests/`? If not, do not proceed.

## Phase 1 — SAT morning: baseline and bounded tool use

- [ ] **1.1** Understand and run the starter's current report pipeline. Document how it searches, fetches, summarizes and writes.
- [ ] **1.2** Add `data/synthetic/` with **8–12 original synthetic evidence records** (different viewpoints). Each needs ID, source type, date, statement, and any hard policy rule.
- [ ] **1.3** Add `research_agent/research_tools.py` for a read-only document/evidence search tool. Verify matching and no-match cases.
- [ ] **1.4** Add a limited model-driven action/observation loop (ReAct-style). All model-selected actions must be parsed and validated against an allowed tool list.
- [ ] **1.5** Add a maximum tool-call limit (initially 3–5); maintain short-term session state and record actions/observations.
- [ ] **1.6** Run one real OpenRouter model-call smoke test and save model ID + observed response; never commit key.
- [ ] **1.7** Test successful retrieval, unknown tool, no evidence, and max steps. Save trace and GitLab commit.

**STOP GATE B:** One user question causes a real LLM-selected allowed tool call; tool result appears in the observation trace. Invalid calls are rejected, and the loop always terminates.

## Phase 2 — SAT afternoon: RAG and source grounding

- [ ] **2.1** Add `research_agent/rag.py` using a small sentence embedding model (e.g., `all-MiniLM-L6-v2`).
- [ ] **2.2** Index the synthetic record texts; preserve source IDs and metadata in retrieval results.
- [ ] **2.3** Begin with **top 3** matches; log similarity scores. Apply a tested minimum relevance rule rather than assuming any top 3 are relevant.
- [ ] **2.4** Compare keyword retrieval and semantic retrieval on paraphrased questions.
- [ ] **2.5** Show that a synthetic *human approval* policy appears in a retrieved answer and in its source references. Show an unrelated question that causes an **insufficient evidence** response.
- [ ] **2.6** Preserve prompt-only baseline and RAG-grounded answer for one question; record exactly what changed.
- [ ] **2.7** Add retrieval tests and save GitLab commit.

**STOP GATE C:** Semantic retrieval works in Colab, citations map to real IDs in the synthetic corpus, and missing sources don't become invented facts.

## Phase 3 — SUN morning: alternatives, coordination and guardrails

- [ ] **3.1** Add a simple candidate comparison with **three approaches**: rules, RAG-assisted categorization and human-reviewed agentic triage.
- [ ] **3.2** Implement a bounded ToT-inspired **beam-width 2 / depth 2** exploration using the Week 4 weighting. Record candidate scores, criteria and pruned options.
- [ ] **3.3** Enforce **hard constraints first** (e.g. mandatory human approval for high-severity incidents). Do not allow weighted score to override them.
- [ ] **3.4** Create four logical roles: planner, researcher, evaluator and report writer, with structured messages and bounded feedback routing.
- [ ] **3.5** Add source diversity checks, evidence-missing flags and escalation/abstention rules.
- [ ] **3.6** Add audit trace (JSON/JSONL): prompts/task summary, actions, tool names, source IDs, scores, stop reasons and human-review flags. Exclude API keys and sensitive data.
- [ ] **3.7** Run tests demonstrating that the evaluator can reject a noncompliant option and request one bounded follow-up.

**STOP GATE D:** A full question-to-report run completes, shows alternatives and source IDs, respects human approval, and produces a trace. If it doesn't, stop feature work and fix this before decorating the app.

## Phase 4 — SUN afternoon: evaluation and deliverables

- [ ] **4.1** Build an 8–10 question evaluation set with expected source IDs, hard constraints, and known gaps.
- [ ] **4.2** Compare prompt-only vs retrieval single-agent vs full pipeline on identical cases. Record observed results; no fabricated benchmarks.
- [ ] **4.3** Measure at least: question coverage, correctly cited claims, mandatory requirement compliance, escalation success, wall-clock latency and total model calls. Flag synthetic-data limitations.
- [ ] **4.4** Run complete Colab notebook from a clean session. Rerun automated tests and save visible outputs/trace.
- [ ] **4.5** Finish `README.md` with architecture, quick start, examples, commands, limitations, testing and checkpoint-to-code table.
- [ ] **4.6** Update `docs/DESIGN_DECISIONS.md`, `docs/BUILD_LOG.md`, `docs/CHECKPOINT_MAPPING.md`. Be explicit about what is implemented vs planned.
- [ ] **4.7** Publish/import repository to **public GitHub** (CMU requirement). Verify README, notebook, sample data, tests and run steps anonymously. GitLab can remain your main private workspace.
- [ ] **4.8** Write the **1,000–1,500-word report** following CMU's template and link GitHub.
- [ ] **4.9** Prepare **8–10 slides**: problem, why agents, architecture, evolution, demo, retrieval and ToT, multi-agent/safety, results, limitations, repository.
- [ ] **4.10** Record an **8–10-minute** presentation with an authentic end-to-end demo (live or from previously captured genuine run); record and upload to a host accessible by reviewers.
- [ ] **4.11** Prepare a short separate video-link document with a **2–3 sentence summary**.
- [ ] **4.12** Open the video link in a separate browser/private window; test audio, visibility and sharing; attach report and video-link document in Canvas well before Monday, 23 November 2026 at 9:29 AM MST.

**STOP GATE E:** The GitHub repo is public and runnable/reviewable; report is PDF or DOCX; presentation video is accessible and 8–10 min; evaluation claims match observed tests; Canvas upload is complete.

## If time runs short — priority order

1. **Protect first:** end-to-end working agent, working Colab notebook, accurate report, video and GitHub link.
2. **Then:** measured retrieval, trace, basic safety and four logical agent roles, minimal ToT comparison.
3. **Optional:** polished web UI, public web scraping, MCP server, sophisticated persistent database, extensive benchmarks, advanced model providers, optional 90-second elevator pitch.

## Source and credibility rules

- All mock company policies, incident events and performance values must be marked synthetic.
- Do not describe a static Python decision tree as an LLM making autonomous choices; explicitly mark mock and live model modes.
- The uploaded ScienceDirect articles predominantly concern additive manufacturing, not incident triage; don't mix them into the test corpus.
- Never put OpenRouter keys in notebooks, source files, `.env.example`, logs, GitLab or GitHub. Use Colab **Secrets** or protected environment variables.
- Check your program's academic AI-assistance rules and acknowledge attribution and external assistance as required. Do not backdate commits or invent activity/results.

## How to request troubleshooting help

At any stop gate, share **only** (1) gate letter and step number, (2) the exact error or output copied from Colab, and (3) the names of files touched. Never send API keys.

Example: `Gate A, step 0.5 — ImportError ... — README.md, requirements.txt unchanged.`

## Build log (fill as you work)

| Actual date/time | Step | File(s) changed | Test command | Result | What I learned/decision |
|---|---|---|---|---|---|
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

