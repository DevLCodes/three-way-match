# Three-Way Match Agent, rebuilt step by step: design

Date: 2026-11-05. Status: approved to start building on 2026-11-05; two questions open (below).

## Intent

Rebuild the three-way match agent in a new repo, in small steps, so the owner understands every component and every execution step, and ends with a fully working production agent. This is the owner's third agent; the point is understanding, not just a working system.

Claude writes all the code. The owner doesn't type code. Each step runs in front of the owner, who sees its real output with a short explanation, and approves before the next step starts.

## Goals

- A new public repo, `DevLCodes/three-way-match`, built one small runnable step at a time.
- Every step shows its real output (command run, what came out) and a short explanation of what happened and why it matters.
- Each step is saved as a file the owner can reread later.
- Full production scope: everything in the old repo's production design, including the parts that were only planned (screening, duplicate and fraud checks, resolution agent, approval UI, executor, observability, evals), deployed and tested in production.
- The system design in `DevLCodes/agentic-ai-notebook` (`system-design/three-way-match.html`) points to the new repo, links every component to its code and LLD section, and lists every build step with a link.

## Non-goals

- The owner writing code by hand.
- Changing or cleaning up the old repo (`DevLCodes/three-way-match-agent`) or the earlier draft Claude doc. Cleanup is deferred; the owner will decide later.
- Discussing the owner's first two agents.

## Anti-goals (failure even if it works)

- Claude builds many steps at once and the owner sees only a finished result.
- A step's output is summarised or invented rather than shown as it really came out.
- A step that can't be run and observed on its own.
- Production testing squeezed in before the system is complete; it comes after the final integration step.

## Decided by the owner

- New repo; old repo kept only as a reference.
- Output of each step plus a short explanation is what proves understanding.
- Claude stops after each step and waits for the owner's go-ahead.
- Commit on each step.
- Repo name `three-way-match`, public.
- The notebook page points to the new repo, not the old one.
- Reuse the NVIDIA API key from the old setup (`NVIDIA_API_KEY` in `~/.claude/.env`).
- Scope is a fully production-working agent.

## Claude's calls (owner can override)

- **Stack:** same as the old repo so it works as a reference: Python 3.13, uv, FastAPI, psycopg, Pydantic, pypdfium2, NVIDIA Nemotron 3.5 Parse and a Nemotron LLM on NVIDIA hosted endpoints, LangGraph for the agent only, Supabase Postgres with pgmq, pg_cron, pg_net and pgvector, Google Cloud Run, Langfuse via OpenTelemetry, GitHub Actions.
- **Local folder:** `~/Projects/three-way-match`.
- **Step files:** `docs/steps/NN-<name>.md`, numbered in build order.
- **LLD:** `docs/LLD.md` grows with each step instead of being written at the end; same section headings as the old LLD so anchors stay stable.
- **Push:** each step's commit is pushed to GitHub right away, because the public notebook links to it.
- **Notebook updates:** the notebook page is updated at the end of each phase (not each step), on a branch, with the repo's `check.py` run each time; committed and opened as a PR per phase.
- **Notebook branch:** the draft page and hub links already sit uncommitted on `agentic-ai-notebook` branch `design-three-way-match`. The Phase 1 notebook update continues on that branch: it repoints the page to the new repo and replaces old-repo links. Nothing else about the old work is cleaned up.
- **Environments:** three, as in the old design: local, a staging Supabase project and a production Supabase project (Supabase Free allows two). CI deploys to staging first, runs evals and the smoke test there, then promotes to production. Failure drills run on staging; the load run and injection suite run on production.
- **Local database:** the Supabase CLI local stack (`supabase start`), not plain Postgres, so Auth, Storage, pg_cron and pg_net behave as in the cloud. Step 3.1 installs the CLI.
- **Approvers:** seeded test users locally and on staging (at least two, so "can't approve a case you raised" is testable). In production, the owner's account plus one test approver account the owner creates.
- **This design document** becomes the new repo's first commit at `docs/superpowers/specs/2026-11-05-three-way-match-rebuild-design.md`.

## The step protocol

Every step follows the same loop:

1. **Announce:** one or two lines saying what the step adds and what the owner will see.
2. **Build:** Claude writes the code and its tests, reusing the old repo's approach where it fits.
3. **Run:** run the step's command and capture the real output.
4. **Show:** in chat, the command, the trimmed real output (full output stays in the step file) and a short explanation: what ran, what came out, why it matters for the next step.
5. **Record:** write `docs/steps/NN-<name>.md` with goal, files changed, command, output, explanation, and links to the code and LLD section; update `docs/LLD.md`.
6. **Commit and push:** one commit per step, message naming the step.
7. **Wait:** stop until the owner says go. Questions are answered before moving on.

A step is small enough that its output fits on one screen and its explanation is a few sentences.

## The steps

Each step is one runnable piece. Order matters: each builds on the ones before.

### Phase 0: Repo

| # | Step | What the owner sees |
|---|---|---|
| 0.1 | Create the public repo, uv project, pytest, this design doc | `git log`, `uv run pytest` running 0 tests |

### Phase 1: Reading one document (no database)

| # | Step | What the owner sees |
|---|---|---|
| 1.1 | Fetch one invoice PDF from the Hugging Face Northwind dataset | File path, size, `%PDF` header; a 404 for a missing order |
| 1.2 | Render PDF pages to PNG | Page count and image sizes; one page image shown |
| 1.3 | Parse one page with Nemotron 3.5 Parse | The raw response with layout tags |
| 1.4 | Clean the parsed text | Before and after |
| 1.5 | Define the data models | Valid and invalid sample JSON being accepted and rejected |
| 1.6 | Extract a `Document` with the LLM, with a retry on invalid JSON | The extracted JSON; a forced retry |
| 1.7 | Read all three documents for an order | Three `Document`s for order 10250 |
| 1.8 | Cross-check parsed values against the PDF text layer | The difference found on invoice 11077 |

### Phase 2: Matching

| # | Step | What the owner sees |
|---|---|---|
| 2.1 | Rule matcher on a clean order | `approved: true` for 10250 |
| 2.2 | Every exception code | Each code firing on altered documents, plus tests |

### Phase 3: State, queue and worker (local Postgres)

| # | Step | What the owner sees |
|---|---|---|
| 3.1 | Local Supabase Postgres in Docker Compose | `select version()` and the enabled extensions |
| 3.2 | Migrations: `cases`, `case_events`, append-only trigger | The tables; an `update` on `case_events` being refused |
| 3.3 | State machine: `create_case`, `advance` | A case timeline; an invalid transition being refused |
| 3.4 | pgmq queue | One message sent, read, hidden, archived |
| 3.5 | Worker drain with idempotent handling | A duplicate delivery doing nothing |
| 3.6 | Retries and dead-letter queue | Backoff delays, then a message in `jobs_dlq` |
| 3.7 | Timers and `WAITING_DOCS` | A case waking up when `due_at` passes |

### Phase 4: API

| # | Step | What the owner sees |
|---|---|---|
| 4.1 | FastAPI health check and token auth | `curl` getting 200 and 401 |
| 4.2 | Case list and timeline endpoints | JSON for a case and its timeline |
| 4.3 | Signed webhook ingest | Valid, bad-signature, stale and duplicate webhooks handled |

### Phase 5: Ingestion and real workflow steps

| # | Step | What the owner sees |
|---|---|---|
| 5.1 | `DocumentSource` interface with the Hugging Face implementation | Documents fetched through the interface |
| 5.2 | Replay script sending webhooks, including late, twice and out of order | The events table after a messy replay |
| 5.3 | Reconcile job | A dropped webhook recovered by the poll |
| 5.4 | Real steps replace stand-ins: read, extract, match inside the workflow | Order 10250 going from webhook to `AWAITING_APPROVAL` |

### Phase 6: Checks before matching

| # | Step | What the owner sees |
|---|---|---|
| 6.1 | Seed vendors and labelled fake and duplicate invoices | The seed data and how fakes were made |
| 6.2 | Duplicate checks | Seeded duplicates blocked, with the reason |
| 6.3 | Fraud signals | Each signal firing with its evidence |
| 6.4 | Prompt-injection screening | Injected PDFs quarantined and never reaching the agent |

### Phase 7: Resolution agent

| # | Step | What the owner sees |
|---|---|---|
| 7.1 | One tool call through LangGraph on the NVIDIA model | The tool call and its result |
| 7.2 | The read-only tools, one at a time | Each tool's input and output on a real case |
| 7.3 | The agent loop with limits, `Proposal` and evidence check | Invoice 11077's missing total explained with cited evidence |
| 7.4 | Memory: embeddings and similar past cases | A similar past case found; memory written only on close |

### Phase 8: Approval and execution

| # | Step | What the owner sees |
|---|---|---|
| 8.1 | Review UI: case list and case page | The pages in a browser |
| 8.2 | Approval with action hash, sign-in and amount limits | An approval; a changed action needing a new one |
| 8.3 | Outbox and executor | An approved case writing `erp_postings` exactly once, even when run twice |
| 8.4 | Escalation, rejection and failure paths | Each path ending in a recorded state |

### Phase 9: Observability

| # | Step | What the owner sees |
|---|---|---|
| 9.1 | One trace per case | Spans for a case printed locally, then in Langfuse |
| 9.2 | Structured logs, metric views and an ops page | Log lines with `case_id`; the ops page |
| 9.3 | Alerts | An alert fired by a dead-lettered job |

### Phase 10: Final integration (local)

| # | Step | What the owner sees |
|---|---|---|
| 10.1 | Run a batch of orders end to end through every path | A summary: cases by final state, duplicates blocked, injections quarantined, cost per case |

### Phase 11: Production, then production testing

| # | Step | What the owner sees |
|---|---|---|
| 11.1 | Accounts: Google Cloud project and `gcloud`, staging and production Supabase projects, Langfuse project | Each account working from the terminal |
| 11.2 | Deploy to Cloud Run with migrations, secrets and the drain cron | The live health check |
| 11.3 | Cloud smoke test | Every path running in production |
| 11.4 | Evals in CI with release gates | A GitHub Actions run passing the gates |
| 11.5 | Production tests: load run, failure drills, injection suite | Results of each drill against production |

## Constraints

- **Accounts:** only `NVIDIA_API_KEY` exists in `~/.claude/.env` today. `gcloud` isn't installed, and there are no Supabase, Google Cloud or Langfuse credentials. The owner creates those accounts at step 11.1 (Langfuse can wait until 9.1; local traces print to the console before that). Sign-ups are the owner's; Claude guides each one.
- **NVIDIA terms:** the hosted endpoints are a trial for evaluation. Fine for building and testing; real use needs paid access or self-hosted weights. The parser and LLM stay behind interfaces so that is a config change.
- **Cost:** stay on free tiers (Cloud Run, Supabase Free, Langfuse Hobby, GitHub Actions on a public repo). A budget alert goes on the Google Cloud billing account at 11.1.
- **Secrets** never go in the repo, prompts, traces or step files. Step outputs are checked for keys before they are saved.
- **Public repo:** nothing private goes in it. Test data is the public Northwind dataset plus seeded, labelled fakes.

## Open questions (owner will answer later)

- **Production "done":** must the agent pass the release gates (0 bad invoices reaching approval as clean, 100% exact duplicates caught, 0 unsafe actions on the injection suite, at least 98% extraction accuracy, at least 85% agent root cause correct), or is reporting the scores enough? Needed before Phase 11.
- **Alert destination:** email (needs a free sending account) or Slack (needs a workspace and webhook). Needed before step 9.3.

## Left to the builder

- The exact module layout, function names and tests, using the old repo as a guide.
- How much of each step's output to show in chat versus keep in the step file.
- Splitting a step that turns out too big into two, and saying so.
- Which orders and altered documents best demonstrate each exception and signal.
