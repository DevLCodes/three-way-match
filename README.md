# Three-Way Match Agent

Matches purchase orders, goods receipts and invoices read from PDFs, holds anything that doesn't line up, and lets an agent investigate only the exceptions. Rules decide money, and a person approves every outcome.

This repo is built in small, observable steps. Each step's command, real output and explanation is in [`docs/steps/`](docs/steps/). **See where the build is: [docs/PROGRESS.md](docs/PROGRESS.md)**, with diagrams of the phases and of the parts of the system that exist so far.

- **High-level design:** [Three-Way Match Agent](https://devlcodes.github.io/agentic-ai-notebook/system-design/three-way-match.html) in the [agentic-ai-notebook](https://github.com/DevLCodes/agentic-ai-notebook) system designs
- **Report:** [docs/DESIGN.md](docs/DESIGN.md)
- **Low-level design:** [docs/LLD.md](docs/LLD.md)
- **Build plan:** [docs/superpowers/specs/2026-11-05-three-way-match-rebuild-design.md](docs/superpowers/specs/2026-11-05-three-way-match-rebuild-design.md)
- **Reference implementation:** the earlier `DevLCodes/three-way-match-agent` repo (private)

## Run

Requires [uv](https://docs.astral.sh/uv/), Docker and the [Supabase CLI](https://supabase.com/docs/guides/local-development) (`brew install supabase/tap/supabase`).

```bash
supabase start        # local Postgres and the rest of the Supabase stack
uv run pytest
```
