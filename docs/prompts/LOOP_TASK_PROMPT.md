# Loop Task Prompt

Version: 1.0
Date: 2026-05-19

Use this prompt for each Codex development-loop iteration. It is intentionally compact; task detail lives in `docs/tasks.md`.

---

## Objective

Implement the `Next Task` named in `docs/CODEX_PROMPT.md`.

Work one task at a time. Continue to the next task only after verification is green and state files are updated, unless a stop condition exists.

---

## Required Read Order

1. `docs/CODEX_PROMPT.md`
2. The assigned task block in `docs/tasks.md`
3. `docs/IMPLEMENTATION_CONTRACT.md`
4. Task-specific source files listed under `Files:`
5. Eval artifacts only when the task type or acceptance criteria touch RAG, tools, agent behavior, metrics, or operator outcomes

Do not read archived prompts or archived task graphs unless the active task needs historical acceptance evidence.

---

## Implementation Rules

- Keep runtime tier T1 unless an ADR explicitly changes it.
- Implement only the assigned task scope plus necessary adjacent support.
- Add or update tests for every acceptance criterion.
- Preserve tenant isolation, SQL parameterization, PII redaction, auditability, and human-approval boundaries.
- Prefer existing repository patterns over new abstractions.
- Do not commit unless the user explicitly asks.

---

## Verification

Run the narrow task tests first, then the repo baseline:

- `.venv/bin/python -m pytest tests/ -q --tb=short`
- `.venv/bin/ruff check src/lead_sla_agent tests`
- `.venv/bin/ruff format --check src/lead_sla_agent tests`

Also run `ruff` checks for `alembic` when database or migration files change.

---

## State Updates

After a passing task:

- Update `docs/CODEX_PROMPT.md` with the new baseline and next task.
- Append concise evidence to `docs/IMPLEMENTATION_JOURNAL.md`.
- Update `docs/EVIDENCE_INDEX.md` only for durable or canonical proof.
- Write a phase review under `docs/audit/` when the phase completes.

If blocked, write the blocker to `docs/CODEX_PROMPT.md` Fix Queue and stop.
