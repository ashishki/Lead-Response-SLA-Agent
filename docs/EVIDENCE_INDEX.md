# Evidence Index - Lead Response SLA Agent

Version: 1.0
Last updated: 2026-05-19

This file indexes durable proof so agents can retrieve prior evidence quickly. It is not authoritative by itself; every row points to the artifact that carries the evidence.

---

## Evidence Table

| Topic / Finding / Task | Artifact type | Location | Scope covered | Last verified | Canonical? |
|------------------------|---------------|----------|---------------|---------------|------------|
| RAG baseline plan | eval | `docs/retrieval_eval.md` | Retrieval metrics, dataset plan, regression policy | 2026-05-19 | Yes |
| Tool-Use baseline plan | eval | `docs/tool_eval.md` | Tool schema and side-effect eval scenarios | 2026-05-19 | Yes |
| Agent loop baseline plan | eval | `docs/agent_eval.md` | Agent termination, handoff, and allowed-action eval scenarios | 2026-05-19 | Yes |
| NFR baseline plan | nfr | `docs/nfr.md` | Latency and operational targets for pilot | 2026-05-19 | Yes |
| Bootstrap decisions | decision log | `docs/DECISION_LOG.md` | Initial solution shape, profiles, runtime, retrieval mode, approval boundaries | 2026-05-19 | No |
| Bootstrap handoff | journal note | `docs/IMPLEMENTATION_JOURNAL.md` | Session-level continuity for the generated Phase 1 package | 2026-05-19 | No |

---

## Retrieval Rules

- Prefer rows that match the current task's `Context-Refs`, open findings, or active profile tags.
- If an evidence row points to a stale or missing artifact, fix the artifact or remove the row.
- Do not treat a journal note as proof when a test, eval, or review report exists.
