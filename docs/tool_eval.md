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
| Tool schema version | `tool-schema-v1` |
| Registered tools | `send_message`, `create_or_update_lead`, `lookup_available_slots`, `book_slot`, `lookup_lead_history`, `create_human_review_task` |
| Write tools | `send_message`, `create_or_update_lead`, `book_slot`, `create_human_review_task` |
| Side-effect classes | read, write, send, book |
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
| 2026-05-19 | T11 | `tool-schema-v1` | catalog metadata, missing idempotency key, unsafe message gate | schema validation pass rate=100%; unsafe-gate pass rate=100%; idempotency rejection pass rate=100% | pass | Provider timeout fallback remains pending T12 adapter tests. |
| 2026-05-19 | T12 | `tool-schema-v1` | fake messaging send, fresh-slot booking gate, CRM idempotency, timeout fallback documentation | call success rate=100%; schema validation pass rate=100%; unsafe-gate pass rate=100%; provider timeout fallback scenario documented | pass | Fake adapters require no real provider credentials. |

---

## Open Tool Findings

none

---

## Regression Notes

none
