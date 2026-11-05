# Three-Way Match Agent: Report

High-level design: [https://devlcodes.github.io/agentic-ai-notebook/system-design/three-way-match.html](https://devlcodes.github.io/agentic-ai-notebook/system-design/three-way-match.html). Low-level design: [LLD.md](LLD.md). Build plan: [rebuild design](superpowers/specs/2026-11-05-three-way-match-rebuild-design.md).

## What it does

Reads a purchase order, a goods receipt and an invoice from PDFs, matches them with fixed rules, and holds anything that doesn't line up for a person to approve. An LLM agent investigates only the exceptions, with read-only tools. See [the problem](https://devlcodes.github.io/agentic-ai-notebook/system-design/three-way-match.html#problem).

## Rules the design holds

1. Code decides money. No LLM output can approve an invoice.
2. Documents are untrusted data, never instructions.
3. The agent proposes; a separate executor acts, only with a human approval.
4. Every step is safe to run twice.
5. Every state change is recorded in an append-only log.
6. Document source, parser and LLM sit behind interfaces.

## Components

Each row links to its section of the high-level design. Code links are added as each step builds the component.

| Component | HLD section | Built in phase |
|---|---|---|
| Document reading: fetch, render, parse, extract | [Reading documents](https://devlcodes.github.io/agentic-ai-notebook/system-design/three-way-match.html#reading) | 1 |
| Rule matcher | [Matching rules](https://devlcodes.github.io/agentic-ai-notebook/system-design/three-way-match.html#matching) | 2 |
| Case state machine | [Case lifecycle](https://devlcodes.github.io/agentic-ai-notebook/system-design/three-way-match.html#lifecycle) | 3 |
| Job queue and worker | [Queue, retries and scale to zero](https://devlcodes.github.io/agentic-ai-notebook/system-design/three-way-match.html#queue) | 3 |
| API and webhook ingest | [Architecture](https://devlcodes.github.io/agentic-ai-notebook/system-design/three-way-match.html#architecture) | 4, 5 |
| Duplicate, fraud and injection checks | [Architecture](https://devlcodes.github.io/agentic-ai-notebook/system-design/three-way-match.html#architecture) | 6 |
| Resolution agent | [The resolution agent](https://devlcodes.github.io/agentic-ai-notebook/system-design/three-way-match.html#agent) | 7 |
| Approval UI and executor | [Approval and execution](https://devlcodes.github.io/agentic-ai-notebook/system-design/three-way-match.html#approval) | 8 |
| Observability and evals | [Observability and evals](https://devlcodes.github.io/agentic-ai-notebook/system-design/three-way-match.html#observe) | 9, 11 |
| Deployment | [Deployment](https://devlcodes.github.io/agentic-ai-notebook/system-design/three-way-match.html#deploy) | 11 |

## Decisions

| Decision | Choice | Why |
|---|---|---|
| Orchestration | Postgres state machine, queue in the same database (pgmq) | A state change and its next job commit together |
| Agent scope | Exceptions only, LangGraph for that one loop | Cheaper, repeatable, smaller attack surface |
| Fraud and duplicate decisions | Deterministic rules with evidence | Testable and auditable |
| Approval | A person approves every case in v1 | Safe until evals earn trust |
| Hosting | Cloud Run (scale to zero) and Supabase Free | Near-zero cost |

## Build order

Built in small observable steps; each step's output and explanation is in [steps/](steps/). The full ordered list is in the [build plan](superpowers/specs/2026-11-05-three-way-match-rebuild-design.md#the-steps).
