# Lead Response SLA Agent - Project Plan

Status: paused reference implementation
Role: lead-response and SLA workflow example
Priority: P2

## Strategic Role

Lead Response SLA Agent is technically useful but should pause unless a real
service business, real lead flow, or operator is available.

Without real CRM data, booked-call pressure, and response-time baseline, it is a
demo rather than an active product.

## Near-Term Roadmap

### P0 - Pause Cleanly

- Mark as paused/reference in README.
- Preserve architecture, evals, and runbook as reusable evidence.

### P1 - Extract Reusable Patterns

- Move useful patterns into Workflow-to-Agent Studio examples:
  - lead intake workflow
  - deterministic acknowledgment
  - RAG-safe answers
  - human handoff
  - CRM side effects
- Reuse permission/tool-use lessons in Training OS scenarios.

### P2 - Resume Only With Real Business

- Reopen if a real lead source and operator appear.
- Measure baseline response time and conversion before adding features.

## AI-Development Tasks

- No speculative agent features.
- If resumed, require real pilot metrics and evals before implementation.

## Stop Conditions

- Do not simulate business traction.
- Do not add CRM complexity without a real CRM target.
