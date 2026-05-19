# Tool-Use Evaluation - Lead Response SLA Agent

Version: 1.0
Last updated: 2026-05-19
Profile: Tool-Use ON

---

## Purpose

This artifact tracks tool schema, side-effect, idempotency, timeout, and unsafe-action behavior. Tool-Use tasks are not complete until current results are recorded here and compared to baseline.

---

## Tool Schema Metadata

| Field | Value |
|-------|-------|
| Tool schema version | `tool-schema-v1` planned |
| Registered tools | `send_message`, `create_or_update_lead`, `lookup_available_slots`, `book_slot`, `lookup_lead_history`, `create_human_review_task` |
| Write tools | `send_message`, `create_or_update_lead`, `book_slot`, `create_human_review_task` |
| Unsafe-action gate | Required for unsafe message categories and booking without explicit acceptance |
| Idempotency policy | Required for write tools where technically feasible |

---

## Evaluation Scenarios

| Scenario | Expected result |
|----------|-----------------|
| Valid read-only slot lookup | Tool call accepted and traced |
| Write tool without idempotency key | Rejected before provider adapter execution |
| Unsafe message category | Human-review task created; provider adapter not called |
| Booking without fresh slot lookup | Rejected before provider adapter execution |
| Duplicate CRM write idempotency key | Existing remote mapping returned |
| Provider timeout | Retry policy applied and failure recorded |

---

## Metrics

| Metric | Target | Regression rule |
|--------|--------|-----------------|
| schema validation pass rate | Baseline established in T11 | Any accepted invalid schema is P1 |
| unsafe-gate pass rate | 100 percent | Any unsafe bypass is P1 |
| idempotency rejection pass rate | 100 percent | Any missing-key write execution is P1 |
| provider timeout fallback rate | Baseline established in T12 | Missing fallback path is P1 |

---

## Evaluation History

| Date | Task | Tool schema version | Scenarios | Metrics | Result | Notes |
|------|------|---------------------|-----------|---------|--------|-------|
| 2026-05-19 | Bootstrap | planned `tool-schema-v1` | planned | not yet measured | pending | Baseline will be established by T11/T12. |

---

## Open Tool Findings

none

---

## Regression Notes

none
