# Working in this repo

The owner is learning every component. Build in the small steps listed in `docs/superpowers/specs/2026-11-05-three-way-match-rebuild-design.md`, one at a time. The owner doesn't write code; Claude does.

For every step:

1. Announce in one or two lines what the step adds and what the owner will see.
2. Write the code and its tests. Use `~/Projects/three-way-match-agent` (old repo) as a reference only.
3. Run the step's command and capture the real output. Never invent or paraphrase output.
4. Show the command, the trimmed real output and a short explanation: what ran, what came out, why it matters next.
5. Write `docs/steps/NN.S-<name>.md` (two-digit phase, step number) with goal, files changed, command, full output, explanation, and links to the code and the LLD section. Update `docs/LLD.md`.
6. Check outputs for secrets before saving. Commit once per step and push.
7. Stop and wait for the owner's go-ahead before the next step.

At the end of each phase, update `system-design/three-way-match.html` in `~/Projects/agentic-ai-notebook` (branch `design-three-way-match`) so its build steps and component links point to this repo, and run that repo's `check.py`.

Agentic AI notebook integration: yes
