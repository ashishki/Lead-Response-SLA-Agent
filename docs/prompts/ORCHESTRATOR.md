# Lead Response SLA Agent - Codex Orchestrator

Version: 1.0
Execution mode: Codex-only
Project root: `/home/ashishki/Documents/dev/ai-stack/projects/Lead-Response-SLA-Agent`

This file is the operating prompt for Codex in this repository. There is no Claude Code runtime in this project, and Codex must not invoke Codex through `codex exec` or any nested Codex CLI call. The active Codex session reads state, implements the next task directly, runs verification, and updates the playbook state files.

---

## Hard Rules

- No `codex exec` calls from inside Codex.
- No `.claude/commands/*` entrypoint is required for this project.
- Work from file state, not chat memory: `docs/CODEX_PROMPT.md` and `docs/tasks.md` are the current source of truth.
- Implement one task at a time unless the user explicitly asks otherwise.
- Run the development loop nonstop across phase boundaries. A phase boundary is a checkpoint, review, and state update; it is not a pause by default.
- Continue automatically to the next phase when the phase review has no P0/P1 findings, no eval regression, no architecture/runtime-tier change, and verification is green.
- Do not claim independent review when the same Codex session wrote the code. Record it as a verification pass. Independent review means a fresh Codex session or a human review.
- Do not start implementation if `docs/audit/PHASE1_AUDIT.md` is missing or not `PASS`.
- For profile-tagged tasks, update the matching eval artifact before marking the task done.
- Commit only when the user asks, unless a task prompt explicitly includes committing as part of the assignment.

---

## Mandatory Start Sequence

1. Read `docs/CODEX_PROMPT.md`.
2. Read `docs/tasks.md`.
3. Read `docs/IMPLEMENTATION_CONTRACT.md`.
4. Check `docs/audit/PHASE1_AUDIT.md`:
   - If missing or not `PHASE1_AUDIT: PASS`, stop and report the blocker.
   - If PASS, continue.
5. Check `git status -sb`.
   - If unrelated user changes exist, do not stage or overwrite them.
   - If changes overlap the next task, inspect them and work with them.
6. Determine the next task from `docs/CODEX_PROMPT.md`.

---

## Task Execution Protocol

For the current task:

1. Read only the task block for the assigned task in `docs/tasks.md`.
2. Read the task's `Context-Refs`.
3. Read dependency task summaries only when they affect interfaces or acceptance criteria.
4. Capture baseline:
   - Before T01, tests may not exist; record `0 passing tests (pre-implementation)`.
   - After tests exist, run `python -m pytest tests/ -q`.
   - After the skeleton exists, run `ruff check src/lead_sla_agent tests` and `ruff format --check src/lead_sla_agent tests`.
5. Implement only files in the task's `Files:` scope unless a small adjacent support file is required. If adding adjacent scope, record why in `docs/IMPLEMENTATION_JOURNAL.md`.
6. Add or update tests for every acceptance criterion.
7. Run the relevant tests and lint/format checks.
8. Update profile eval artifacts when the task has trigger tags:
   - `rag:*` -> `docs/retrieval_eval.md`
   - `tool:*` -> `docs/tool_eval.md`
   - `agent:*` -> `docs/agent_eval.md`
   - `plan:*` -> `docs/plan_eval.md` if Planning is ever enabled
9. Update `docs/CODEX_PROMPT.md` with baseline, next task, completed task, open findings, and profile/eval state changes.
10. Add a concise entry to `docs/IMPLEMENTATION_JOURNAL.md`.

---

## Verification Pass

After each task, Codex performs a verification pass. This is not an independent review unless a fresh session or human performs it.

Check:

- Every acceptance criterion has a corresponding test reference and passing test.
- No forbidden contract rule is violated.
- No PII is logged or exposed in errors, traces, metrics, or test snapshots.
- SQL is parameterized.
- Tenant-scoped queries use tenant context.
- Runtime remains T1: no shell/toolchain mutation, privileged workers, or autonomous runtime expansion.
- Deterministic-owned subproblems remain deterministic.
- Human approval boundaries remain enforced.
- Active profile eval artifacts are updated when relevant.

Record verification status in `docs/IMPLEMENTATION_JOURNAL.md`. If a blocker remains, add it to `docs/CODEX_PROMPT.md` Fix Queue and stop.

---

## Nonstop Loop Policy

The default operating mode is continuous execution through the task graph:

1. Finish the current task.
2. Verify it.
3. Update state and evidence.
4. If the phase is complete, run the phase boundary protocol.
5. If no stop condition exists, immediately begin the next task, including the first task of the next phase.

Do not wait for manual confirmation between phases just because the phase number changed. Human approval is required only for stop conditions:

- P0/P1 findings that remain unresolved.
- Failing tests, lint, format, CI, or active profile eval gates.
- Eval regression that is not already justified and accepted.
- Architecture, runtime-tier, governance, active-profile, retrieval-mode, compliance, or security-boundary changes.
- Missing required evidence, audit artifact, or phase review artifact.
- User explicitly asks Codex to pause, stop, or wait.

When a stop condition exists, record the exact blocker in `docs/CODEX_PROMPT.md` Fix Queue and `docs/IMPLEMENTATION_JOURNAL.md`, then report it to the user. Otherwise keep following the loop.

---

## Phase Boundary Protocol

When all tasks in a phase are complete:

1. Run the full test and lint suite available at that point.
2. Run active profile eval tests available at that point.
3. Update `docs/CODEX_PROMPT.md`:
   - baseline
   - completed phase summary
   - next phase / next task
   - open findings
   - eval state
4. Write a phase review artifact under `docs/audit/`, for example `docs/audit/PHASE1_REVIEW.md`.
5. Update `docs/audit/AUDIT_INDEX.md`.
6. Apply the Nonstop Loop Policy:
   - if a stop condition exists, pause and report the blocker;
   - if no stop condition exists, continue directly into the next task.

If independent review is desired, the human should start a fresh Codex session and ask it to review the phase using `docs/audit/PROMPT_0_META.md`, `PROMPT_1_ARCH.md`, `PROMPT_2_CODE.md`, and `PROMPT_3_CONSOLIDATED.md`.

---

## Current Project Defaults

| Item | Value |
|------|-------|
| Test command before skeleton | `python -m pytest tests/ -q` when tests exist |
| Test command after skeleton | `python -m pytest tests/ -q --tb=short` |
| Lint command | `ruff check src/lead_sla_agent tests` |
| Format check | `ruff format --check src/lead_sla_agent tests` |
| Runtime tier | T1 |
| Active profiles | RAG, Tool-Use, Agentic |
| Inactive profiles | Planning, Compliance |

---

## Start Now

If the user asks to continue implementation, execute the Mandatory Start Sequence and begin the `Next Task` from `docs/CODEX_PROMPT.md` directly in the current Codex session. Continue task-by-task and phase-by-phase until a stop condition exists or the task graph is complete.
