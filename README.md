# InsightForge
### AI Research Assistant for Product and Technology Decisions

**CMU Agentic AI Program — Research Assistant Capstone**

## Why I chose this project

For my capstone, I wanted to build a research assistant that could help product managers and technical teams compare different technology options instead of just giving a quick answer to a question.

In many technical decisions, the difficult part is not finding one solution. It is understanding the alternatives, checking whether there is enough evidence, and identifying the risks before recommending something. I wanted InsightForge to help with that research process while leaving the final decision to a person.

I started with a smaller, controlled question: *How should a hypothetical fintech company approach AI-assisted incident classification and routing?* I compared three options:

- Rule-based incident classification
- RAG-assisted classification
- Agentic investigation with human oversight

For that first version, I used eight synthetic research records. I did not use actual company incidents or customer information.

After I had the initial workflow and tests working, I extended InsightForge to research broader product and technology questions using live public-web searches. The live version does not rely on the original incident-triage documents to generate answers.

## What InsightForge does

The live version accepts a research question and works through several stages:

1. **Planner:** Defines three alternatives and prepares search queries.
2. **Researcher:** Searches the public web using Tavily. It also uses a bounded ReAct-style decision to decide whether one more search is needed.
3. **Evidence memory and Critic:** Stores the results from that run in a temporary TF-IDF retrieval index, retrieves relevant evidence, and checks source coverage.
4. **Tree-of-Thought comparison:** Scores the three alternatives using weighted criteria, keeps the top two, and proposes ways to reduce their risks.
5. **Report Writer:** Produces a recommendation with source references and flags it for human review. An invalid citation format can trigger one correction attempt.

The Gradio interface shows the sources, agent timeline, report, and audit information. There is also an **Explain Decision** feature. Once a run is complete, I can ask why an alternative was ranked first. It uses the evidence from that run and makes a new LLM call without searching the web again.

The four agent roles are coordinated **sequentially**, not as four parallel processes. The live ReAct step is deliberately limited; the earlier offline prototype includes a separate multi-step ReAct controller.

## Course concepts I used

| Course topic | How I used it |
|---|---|
| Tool calling | The application runs web research tools and uses their outputs in later stages. |
| ReAct reasoning | A model selects an allowed research action; Python validates and executes it. The original prototype also supports multiple action–observation steps. |
| Knowledge and memory | The original case study compares keyword and semantic retrieval. The live app uses temporary TF-IDF retrieval over newly collected sources. |
| Tree of Thought | Three alternatives are evaluated, with the top two selected for further refinement. |
| Multi-agent coordination | Planner, Researcher, Critic/Evaluator, and Report Writer have separate responsibilities and pass results to each other. |
| Safety | Research is read-only, citations and source IDs are checked, repeated actions are limited, and recommendations require human review. |

I chose bounded steps and read-only tools because I wanted to keep the demo manageable and avoid having a research assistant take actions on real systems.

## What I tested

I kept the evaluation of the original synthetic project separate from the live-web demo because they test different things.

### Original synthetic case study

The earlier controlled evaluation recorded:

| Measure | Result |
|---|---:|
| Automated tests | 41 passed |
| Controlled scenarios after scope validation | 10/10 passed |
| Required-evidence coverage before recovery | 64.6% |
| Required-evidence coverage after recovery | 87.5% |
| Keyword retrieval — top 1 | 7/8 |
| Semantic retrieval — top 1 | 7/8 |
| Both retrieval methods — top 3 | 8/8 |

The additional evidence recovery improved required-evidence coverage by 22.9 percentage points. Both retrieval approaches achieved the same overall scores on this small benchmark. These are results from synthetic examples, not evidence of how the system would perform in a real company's incident workflow.

### Live public-web research

I also tested two different product-management research questions on November 22, 2026:

| Research question | Public sources | LLM calls | Run time | Top-ranked option |
|---|---:|---:|---:|---|
| Which AI feature should a B2B SaaS company prioritize? | 12 | 5 | 17.92 sec | AI onboarding assistant (3.95/5) |
| Should a financial-services company build, buy, or combine AI knowledge-assistant solutions? | 10 | 6 | 13.13 sec | Purchase an existing platform (3.80/5) |

Both runs ended with `ready_for_human_review`. In the second run, the Report Writer initially used incorrectly formatted citations; the validation step caught this and the report passed after one correction. I also tested **Explain Decision** with both research questions.

The scores above are comparisons generated by the model, not measured cost savings, product outcomes, or verified return on investment. The actual audit JSON files are saved in [`evaluation/live_web/`](evaluation/live_web/).

## How to run the project

### Original offline tests

Clone the repository, then install the original dependencies:

```bash
git clone https://github.com/pandirimanvitha/InsightForge.git
cd InsightForge
pip install -r requirements.txt
python -m pytest tests -q
```

These tests use the synthetic case study and do not need an OpenRouter or Tavily key.

### Live research dashboard

Install the live-demo dependencies:

```bash
pip install -r requirements_live.txt
```

Set the following environment variables **outside the repository**:

- `OPENROUTER_API_KEY` — for the research and reporting model
- `TAVILY_API_KEY` — for live public-web searches
- `INSIGHTFORGE_DEMO_PASSWORD` — for the Gradio demo login

For my observed live runs, the primary model was `google/gemini-2.5-flash-lite` through OpenRouter. An optional fallback is `openai/gpt-4.1-mini`. LangSmith tracing can be configured separately.

Then run:

```bash
python demo_ui_strategy_langchain_rag_report_fixed.py
```

Open the Gradio URL and sign in using the username `reviewer` and the password you configured. Enter a product or technology research question, run the analysis, and review the report, sources, timeline, and audit. The Explain Decision tab works after a successful research run in the same browser session.

For more setup details and the optional LangSmith settings, see [`docs/LIVE_DEMO.md`](docs/LIVE_DEMO.md).

## Where the main files are

| Location | Purpose |
|---|---|
| [`demo_ui_strategy_langchain_rag_report_fixed.py`](demo_ui_strategy_langchain_rag_report_fixed.py) | Live dashboard and research workflow |
| [`docs/LIVE_DEMO.md`](docs/LIVE_DEMO.md) | Setup instructions and live-demo details |
| [`requirements_live.txt`](requirements_live.txt) | Additional packages for the live version |
| [`research_agent/`](research_agent/) | Original ReAct, retrieval, evaluation, coordination, and safety components |
| [`data/synthetic/`](data/synthetic/) | Synthetic research evidence |
| [`tests/`](tests/) | Offline automated tests |
| [`evaluation/`](evaluation/) | Controlled benchmarks and live audit files |
| [`notebooks/`](notebooks/) | Google Colab development notebook |

## What worked and what I would improve

The biggest improvement for me was moving from a predefined research example to a version that can generate its own alternatives and search for fresh information. Separating the agent roles also made it easier to see where a result came from and where an error happened. The report citation error in the second live test was a useful example: validation caught the problem instead of accepting the first output.

There are still limitations. Many public search results come from vendors or blogs, and having several different domains does not mean the evidence is independent or balanced. Checking that a citation refers to a real retrieved source also does not prove that the source supports the specific claim. The temporary memory is not a long-term knowledge base, and the live workflow does not run agents in parallel. I have not measured a 90% claim-groundedness target or tested actual business outcomes.

If I continue the project, I would focus on checking claims against full sources, handling conflicting viewpoints, adding more evaluation questions, measuring costs, and making human-review rules more specific.

**InsightForge is a research and decision-support prototype. It does not connect to production incident systems or make operational changes. The final recommendation stays with the human user.**

## Acknowledgments

I started from the CMU Research Agent starter template and used ChatGPT extensively for implementation support, debugging, and documentation as the project developed. I ran and inspected the workflows described here, and I've tried to keep the results and limitations tied to what was actually observed.
