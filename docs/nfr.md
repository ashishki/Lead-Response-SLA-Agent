# Non-Functional Requirements - Lead Response SLA Agent

Version: 1.0
Last updated: 2026-05-19
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

---

## Measurement Rules

- Prefer test and eval artifacts over manual notes.
- Record the dataset, corpus version, and fake/real provider mode for every measured baseline.
- More than 10 percent regression on a latency target is P2 unless safety is affected.
- Any safety regression in unsupported-answer or unsafe-tool behavior is P1.
