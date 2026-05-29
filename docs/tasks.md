# Lead Response SLA Agent Tasks

Status: paused-reference
Last updated: 2026-05-29

Full production-hardening backlog archived at
`docs/archive/portfolio-cleanup-2026-05-29/tasks_full_2026-05-29.md`.

This project is paused as a standalone product unless real business usage or
pilot data appears. Current value is pattern extraction: safe tool use,
human-in-the-loop messaging, tenant isolation, eval fixtures, and rollback
evidence.

## Phase 23 - Pause, Extraction, And Resume Criteria

### T78: Pause Decision And README Alignment

Owner: codex
Type: docs decision
Status: planned

Objective: |
  Align README, project plan, and prompt state with paused/reference status.

Acceptance-Criteria:
  - README and `docs/PROJECT_PLAN.md` state paused/reference status.
  - Resume criteria require real lead data, pilot operator feedback, or a paying
    workflow.
  - No new provider or production-hardening tasks are marked active.

### T79: Reusable Pattern Extraction Pack

Owner: codex
Type: docs integration
Status: planned

Objective: |
  Extract reusable lessons for Workflow-To-Agent Studio and AI Workflow
  Playbook: permission boundaries, human approval, idempotent tools, tenant
  isolation, eval fixtures, and rollback evidence.

Acceptance-Criteria:
  - Extraction pack maps concrete project artifacts to reusable workflow
    patterns.
  - The pack identifies which patterns belong in Workflow-To-Agent Studio,
    Training OS, and AI Workflow Playbook.
  - It does not require copying this product's business domain.

### T80: Resume Criteria Review

Owner: human + codex
Type: review
Status: planned

Objective: |
  Decide whether the project remains paused, becomes a portfolio-only case, or
  resumes due to real business load.

Acceptance-Criteria:
  - Review lists current evidence, missing evidence, and resume triggers.
  - If no real business data exists, next task remains paused.
  - If resumed, the next task is the smallest real-pilot validation step.
