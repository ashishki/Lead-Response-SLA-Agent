# Decision Log - Lead Response SLA Agent

Version: 1.0
Last updated: 2026-05-19

This file is a retrieval index for important decisions. Canonical project documents win if this file conflicts with them.

---

## Rules

- Keep entries short and link to the authoritative document or section.
- Record why a decision was made and what it replaced.
- Update this file when architecture, runtime, governance, profile status, model strategy, or major implementation direction changes.
- Mark superseded decisions explicitly instead of deleting them.

---

## Decision Index

| ID | Date | Status | Decision | Why it matters | Canonical source | Supersedes |
|----|------|--------|----------|----------------|------------------|------------|
| D-001 | 2026-05-19 | Active | Use Hybrid solution shape: deterministic workflow plus bounded conversational/tool agent. | Keeps formalizable safety and SLA behavior deterministic while allowing AI only for language-heavy qualification and replies. | `docs/ARCHITECTURE.md#solution-shape` | none |
| D-002 | 2026-05-19 | Active | Use Standard governance and T1 container/bounded worker runtime. | Customer-facing PII and external side effects justify eval/audit controls, but runtime mutation and privileged autonomy are not needed. | `docs/ARCHITECTURE.md#runtime-and-isolation-model` | none |
| D-003 | 2026-05-19 | Active | Enable RAG, Tool-Use, and Agentic profiles; keep Planning and Compliance profiles OFF. | Retrieval, external tools, and bounded conversation loop are real v1 behavior; structured planning and named compliance frameworks are not launch gates. | `docs/ARCHITECTURE.md#capability-profiles` | none |
| D-004 | 2026-05-19 | Active | Use text-only retrieval for v1. | The pilot corpus is FAQ/policy/pricing text; multimodal retrieval would add cost and eval burden without v1 product need. | `docs/ARCHITECTURE.md#retrieval--embedding-strategy` | none |
| D-005 | 2026-05-19 | Active | Treat unsupported knowledge and unsafe commitments as human-review paths. | Speed is valuable only if the system avoids fabricated policy, regulated advice, and unauthorized business commitments. | `docs/ARCHITECTURE.md#human-approval-boundaries` | none |
| D-006 | 2026-05-19 | Active | Use Codex-only execution; no Claude runtime and no `codex exec` calls from inside Codex. | The project workflow must match the actual operator environment: Codex reads state, implements tasks directly, and records verification without pretending to have an independent Claude orchestrator or spawning a nested Codex process. | `docs/prompts/ORCHESTRATOR.md` | none |
| D-007 | 2026-05-19 | Active | Use Dream Motif Interpreter as a RAG reference, not a dependency. | It provides proven patterns for source contracts, normalized ingestion, pgvector/HNSW, hybrid vector+FTS retrieval, exact recall, insufficient evidence, and eval discipline; this project must adapt them for tenant isolation, PII, and lead-response knowledge. | `docs/RAG_REFERENCE.md` | none |

---

## Retrieval Notes

- Read D-001 through D-007 before changing solution shape, runtime tier, active profiles, retrieval mode, approval boundaries, execution model, or RAG implementation strategy.
- Prefer task `Context-Refs` when implementing a narrow task.
- Add an ADR for changes that alter immutable contract rules, runtime tier, retrieval mode, active profiles, or governance level.
