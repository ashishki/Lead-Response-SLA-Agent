# Decision Log - Lead Response SLA Agent

Version: 1.0
Last updated: 2026-05-20

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
| D-008 | 2026-05-19 | Active | Run development in a nonstop loop across clean phase boundaries. | Phase boundaries are checkpoints for verification and evidence, not manual pause points. Codex continues to the next task/phase unless a stop condition exists. | `docs/prompts/ORCHESTRATOR.md#nonstop-loop-policy` | none |
| D-009 | 2026-05-19 | Active | Use `local-hash-embedding-v1` as the deterministic T09 ingestion adapter. | T09 needs versioned embedding metadata and idempotent ingestion tests without introducing provider SDKs or credentials; production embedding selection still requires an ADR/eval update. | `docs/retrieval_eval.md#architecture-metadata` | none |
| D-010 | 2026-05-20 | Active | Use OpenAI `text-embedding-3-small` at 1536 dimensions as the v1 production embedding model. | Phase 9 needs a real text embedding provider while keeping deterministic/fake embeddings in normal tests; model or dimension changes require ADR and full reindex. | `docs/adr/ADR-002-production-embedding-provider.md` | none |
| D-011 | 2026-05-20 | Active | Use the authenticated internal JSON operator API as the first pilot console surface. | T32 needs review, approve/edit/send, no-send, and outcome workflows now; a frontend can follow once live operator behavior stabilizes. | `docs/adr/ADR-003-operator-console-surface.md` | none |
| D-012 | 2026-05-22 | Active | Prioritize a public-source vertical showcase before blocked legal/privacy and broad production tasks. | The operator is solo and needs a coherent demo corpus, scenario bank, replay report, and manual target list before real pilot access is likely. | `docs/tasks.md#phase-22---solo-public-vertical-showcase`, `docs/market/open_source_research_protocol.md` | none |

---

## Retrieval Notes

- Read D-001 through D-011 before changing solution shape, runtime tier, active profiles, retrieval mode, approval boundaries, execution model, loop cadence, model strategy, RAG implementation strategy, or the operator console surface.
- Prefer task `Context-Refs` when implementing a narrow task.
- Add an ADR for changes that alter immutable contract rules, runtime tier, retrieval mode, active profiles, or governance level.
