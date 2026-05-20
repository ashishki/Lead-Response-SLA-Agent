# ADR-003: Operator Console Surface

Date: 2026-05-20

## Status

Accepted

## Context

The pilot needs an operator workflow for review queue triage, transcript and evidence inspection, approve/edit/send decisions, no-send decisions, and outcome labels. The system already exposes an authenticated FastAPI operator API, while a production frontend has not been selected.

## Decision

Use an authenticated internal JSON operator console API for the first pilot surface. The API remains the product surface for T32 and supports review listing, approval with edits, no-send decisions, and outcome labels. A browser frontend can be added later against this stable API once live operator behavior shows which layout and shortcuts matter.

## Consequences

- Operator behavior is testable now through integration tests and audit records.
- No frontend framework is introduced before the workflow stabilizes.
- The pilot still requires an internal client, script, or lightweight admin tool to call the API.
- Future frontend work must preserve the same tenant-scoped auth and action audit contract.
