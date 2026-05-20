# Non-Functional Requirements - Lead Response SLA Agent

Version: 1.0
Last updated: 2026-05-20
Status: Draft

---

## SLA Table

| Area | Metric | Target | CI gate threshold | Measurement source |
|------|--------|--------|-------------------|--------------------|
| First response | AI-assisted first-response p95 | below 30 seconds | no CI gate until end-to-end workflow exists | workflow metrics |
| Acknowledgement | deterministic acknowledgement p95 | below 2 seconds | below 3 seconds in integration test path | integration tests and metrics |
| Retrieval | query-time retrieval p95 | below 2 seconds for pilot corpus | below 3 seconds in eval fixtures | `docs/retrieval_eval.md` and eval tests |
| Tool calls | provider fake adapter timeout fallback | fallback recorded within configured timeout | timeout scenario passes | `docs/tool_eval.md` |
| Provider sends | provider send failure rate | below 2 percent in pilot fake-provider path | fake provider sends pass in integration tests | workflow metrics |
| Reliability | failed send fallback | human-review task after retry exhaustion | retry exhaustion test passes | integration tests |
| Safety | unsupported answer behavior | 100 percent `insufficient_evidence` or human handoff | any fabricated answer fails eval | `docs/retrieval_eval.md`, `docs/agent_eval.md` |

---

## Baseline History

| Date | Task | Metrics | Result | Notes |
|------|------|---------|--------|-------|
| 2026-05-19 | Bootstrap | not yet measured | pending | Targets initialized before implementation. |
| 2026-05-19 | T17 | first-response p95 target below 30s; deterministic acknowledgement p95 below 2s; retrieval p95 below 2s; provider send failure rate below 2 percent | initialized | Pilot NFR targets recorded; local fake-provider metrics are test baselines, not scaled production commitments. |
| 2026-05-20 | T36 | first-response latency p50/p95, automation success rate, human-review rate, booked labels, provider send failures | pass | Operator analytics API returns tenant-scoped weekly metrics and a markdown weekly report export; sample fixture p50=3000 ms and p95=10000 ms. |

---

## Pilot Weekly Report Export

T36 adds an authenticated operator analytics endpoint:

`GET /operator/analytics/weekly?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

The response includes:

- `first_response_latency_p50_ms`
- `first_response_latency_p95_ms`
- `automation_success_count` and `automation_success_rate`
- `human_review_count` and `human_review_rate`
- `booked_labels`
- `provider_send_failures`
- `weekly_report` markdown suitable for a pilot weekly report

Sample report fields:

```markdown
# Pilot Weekly Report

Window: 2026-05-01 to 2026-05-07
Lead count: 4
First-response latency p50: 3000.0 ms
First-response latency p95: 10000.0 ms
Automation success rate: 0.50
Human-review rate: 0.25
Booked outcomes: 1
Provider send failures: 1
```

---

## Observability Contract

Metric names and labels are part of the production contract. Labels must never include lead IDs, customer names, emails, phone numbers, message text, provider message IDs, provider user IDs, or transcript text.

| Metric | Type | PII-free labels | Alert threshold |
|--------|------|-----------------|-----------------|
| `first_response_latency_ms` | histogram | `tenant_hash`, `channel` | p95 greater than 30000 ms for 10 minutes |
| `retrieval_latency_ms` | histogram | `tenant_hash`, `corpus_version` | p95 greater than 3000 ms for 10 minutes |
| `retrieval_freshness_age_hours` | histogram | `tenant_hash`, `corpus_version` | greater than 24 hours |
| `provider_send_failure_total` | counter | `provider`, `failure_reason` | greater than 2 percent of sends for 10 minutes |
| `sla_breach_total` | counter | `tenant_hash`, `channel` | any sustained increase above pilot baseline for 15 minutes |
| `insufficient_evidence_total` | counter | `tenant_hash`, `reason` | greater than 20 percent of inbound leads for 30 minutes |
| `tool_call_failure_total` | counter | `tool_name`, `failure_reason` | greater than 5 percent of tool calls for 10 minutes |
| `queue_depth` | gauge | `queue_name` | greater than 100 pending jobs or growing for 15 minutes |
| `health_dependency_status` | gauge | `dependency` | any required dependency unhealthy for 5 minutes |

Dashboard panels:

- First-response p50/p95 by tenant hash and channel.
- Provider send failures by provider and failure reason.
- SLA breaches by tenant hash and channel.
- Retrieval freshness age and retrieval latency.
- Insufficient-evidence rate.
- Tool-call failures by tool and failure reason.
- Queue depth by queue.
- Dependency health status.

---

## Measurement Rules

- Prefer test and eval artifacts over manual notes.
- Record the dataset, corpus version, and fake/real provider mode for every measured baseline.
- More than 10 percent regression on a latency target is P2 unless safety is affected.
- Any safety regression in unsupported-answer or unsafe-tool behavior is P1.
