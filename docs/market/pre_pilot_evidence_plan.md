# Pre-Pilot Evidence Plan

Status: active
Date: 2026-05-25
Scope: DFW emergency garage door repair

## Purpose

This package exists because T67 real-data eval is blocked until a human supplies
or approves de-identified pilot transcripts, operator corrections, provider
failure/retry cases, and human approval metadata.

The pre-pilot package proves controlled behavior before live traffic. It does
not prove production ROI, conversion lift, live-client outcomes,
autonomous-send safety, or paid production readiness.

## Evidence Levels

| Level | Artifact | What It Proves | What It Does Not Prove |
|---|---|---|---|
| Public source grounding | `docs/market/public_corpus/garage_door_repair_source_register.md` | Scenario assumptions use public business/market evidence or explicit assumptions. | Private customer behavior or booked-job impact. |
| Controlled scenario coverage | `tests/eval/fixtures/garage_door_leads.json` | 50 synthetic cases cover urgent, routine, pricing, duplicate, provider failure, CRM failure, spam, legal-ish, and policy-missing cases. | Real lead distribution. |
| Replay safety | `docs/market/demo_replays/pre_pilot_replay_report.json` | Human approval is required and unsafe autonomous sends remain zero in controlled replay. | Autonomous send safety in production. |
| Baseline comparison | `docs/market/demo_replays/baseline_comparison_report.json` | Agent/RAG/tool gates handle controlled cases better than brittle baselines. | ROI, conversion lift, or statistically significant lift. |
| Failure-mode replay | `docs/market/demo_replays/failure_mode_replay_report.json` | Provider/CRM/policy failures route to human review without confirmed sends or dropped leads. | Real provider outage frequency. |
| Expert review readiness | `docs/market/expert_review_rubric.md` | A dispatcher/operator can review drafts without raw customer PII. | Independent validation until a human completes the rubric. |

## Acceptance Gate

- At least 50 scenarios.
- At least 10 scenario categories.
- Baseline modes include `manual_template_baseline`, `llm_no_rag_baseline`,
  and `agent_rag_tool_use`.
- Failure replay has zero confirmed outbound sends, zero dropped leads, and zero
  autonomous sends.
- Buyer-facing docs state that production ROI and live-client proof are not yet
  available.

## Next Proof Step

The next stronger proof is `T67b External Expert Review`: one dispatcher,
operator, owner, or local-services consultant scores 30-50 controlled cases
using `docs/market/expert_review_rubric.md`.
