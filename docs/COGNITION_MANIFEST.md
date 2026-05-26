# Cognition Manifest - Lead Response SLA Agent

---
artifact_kind: retrieval_manifest
project: lead-response-sla-agent
source_repo: Lead-Response-SLA-Agent
status: active
canonical: false
generated: false
tags: [rag, tool-use, agentic, multi-tenant, cognition]
---

Version: 1.0
Last updated: 2026-05-25

## Purpose

Repo-local memory map for a high-risk multi-tenant lead response workflow: retrieval, unsafe tools, bounded agent loop, tenant isolation, pilot evidence, and review continuity.

## Authority Rules

- Canonical repo artifacts win over this manifest.
- Obsidian, generated indexes, and context packets are optional navigation layers.
- Tenant isolation, unsafe-action gates, eval baselines, and P1/P2 closures must be updated in canonical artifacts, not vault notes.

## Project Identity

| Field | Value |
|-------|-------|
| Primary shape | Hybrid workflow with text-only RAG, side-effecting tools, and bounded agent loop |
| Governance level | Strict for tenant/tool/eval boundaries |
| Runtime tier | T1 |
| Active profiles | RAG, Tool-Use, Agentic, governance/audit |

## Canonical Truth

| Surface | Path | Notes |
|---------|------|-------|
| Architecture | `docs/ARCHITECTURE.md` | Runtime, profiles, tenant boundaries |
| Contract | `docs/IMPLEMENTATION_CONTRACT.md` | Hard implementation rules |
| Task graph | `docs/tasks.md` | Execution contract |
| Session state | `docs/CODEX_PROMPT.md` | Baseline, findings, next task |
| Decisions | `docs/DECISION_LOG.md`, `docs/adr/` | ADR lineage |
| Journal | `docs/IMPLEMENTATION_JOURNAL.md` | Handoff continuity |
| Evidence | `docs/EVIDENCE_INDEX.md` | Proof lookup |
| RAG eval | `docs/retrieval_eval.md`, `seed/verticals/garage_door_repair/retrieval_eval.json` | Retrieval/no-answer memory |
| Tool eval | `docs/tool_eval.md` | Tool safety memory |
| Agent eval | `docs/agent_eval.md` | Loop and handoff memory |
| Security/runbooks | `docs/security/`, `docs/runbook.md`, `docs/support/` | Operational controls |
| Audits | `docs/audit/` | Review findings |

## Retrieval Scopes

| Scope | Start here | Include next |
|-------|------------|--------------|
| Tenant isolation | contract, architecture | RLS tests, audit findings, data retention docs |
| Unsafe tool action | `docs/tool_eval.md` | tool schemas, operator review, audit event store |
| Retrieval no-answer | `docs/retrieval_eval.md` | seed corpus, evidence index, prior review |
| Agent loop change | `docs/agent_eval.md` | conversation loop, handoff criteria, prior findings |
| Pilot evidence | market/pilot docs | demo replay evals, evidence index, runbook |
| Reviewer packet | task ACs, contract | active eval artifacts and ADRs |

## Local/VPS Agent Context Workflow

Agents do not automatically discover the cognition vault. The operator or orchestrator must pass a repo-local manifest, vault project map, or generated context packet path into the agent task.

Expected sibling layout on any machine that runs agents:

```text
ai-stack/
|-- projects/<repo>/
`-- engineering-cognition-vault/
```

Local project work:

```bash
cd ai-stack/engineering-cognition-vault
./scripts/sync_from_projects.sh --no-pull --commit --push
```

Before review, ensure this project has a fresh vault index:

```bash
cd ai-stack/engineering-cognition-vault
./scripts/ensure_fresh_for_project.sh lead-response-sla-agent --no-pull --commit --push
```

VPS project work:

1. Commit and push code, docs, evals, ADRs, findings, or postmortems in this repo.
2. Refresh the vault on the machine that owns vault sync:

```bash
cd ai-stack/engineering-cognition-vault
git pull --ff-only
./scripts/sync_from_projects.sh --commit --push
```

If an agent runs on the VPS, clone the vault next to `projects/` and pass packet paths explicitly:

```text
../engineering-cognition-vault/10-projects/<project>.md
../engineering-cognition-vault/90-context-packets/<role>-<project>-<scope>.md
```

Do not write canonical decisions, eval results, or findings directly into the vault. Write them into this repo first, then regenerate the vault.

---

## Known Gaps

| Gap | Impact | Migration step |
|-----|--------|----------------|
| Active dirty work exists | Existing modified files may continue changing | Keep cognition migration additive |
| No standardized packets for high-risk scopes | Review context can become too broad | Generate packets for tenant isolation, tools, and retrieval regressions |

## Generated Artifacts

| Artifact | Path | Policy |
|----------|------|--------|
| Cognition index | `generated/cognition/index.json` | Optional generated artifact |
| Context packets | `docs/context-packets/` | Commit only major review/regression packets |

