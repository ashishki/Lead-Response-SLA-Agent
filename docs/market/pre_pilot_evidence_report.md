# Garage Door Pre-Pilot Evidence Report

Status: generated from controlled evidence
Date: 2026-05-25
Vertical: DFW emergency garage door repair

## Verdict

Ready for founder-led pilot conversations and external expert review. Not ready
to claim production ROI, conversion lift, live-client proof, autonomous-send
safety, or paid production readiness.

## Artifact Map

| Artifact | Purpose |
|---|---|
| `docs/market/pre_pilot_evidence_plan.md` | Evidence levels and claim boundaries. |
| `tests/eval/fixtures/garage_door_leads.json` | 50 public/synthetic controlled lead scenarios. |
| `docs/market/demo_replays/pre_pilot_replay_report.json` | Controlled agent replay with human approval required. |
| `docs/market/demo_replays/baseline_comparison_report.json` | Baseline comparison across template, no-RAG, and agent modes. |
| `docs/market/demo_replays/failure_mode_replay_report.json` | Provider/CRM/policy failure replay. |
| `docs/market/expert_review_rubric.md` | External operator review form. |
| `docs/market/pre_pilot_demo_script.md` | Buyer demo flow. |

## Scenario Coverage

- 50 synthetic controlled scenarios.
- 21 scenario categories.
- 31 human-review handoff cases.
- 19 operator-approval draft cases.
- 7 failure-mode cases.
- 0 autonomous sends.
- 0 unsafe autonomous sends.

Covered categories include urgent, routine, missing fields, supported questions,
unsupported service area, risky safety advice, booking boundaries, commercial
leads, price shoppers, duplicates, angry customers, competitor mentions,
impossible SLA promises, spam, legal-ish requests, provider failures, CRM
failures, contact-ready cases, after-hours cases, missing tenant policy, and
unsafe DIY requests.

## Baseline Comparison

| Mode | Correct next-action rate | Unsafe claim count | Human-approval violations |
|---|---:|---:|---:|
| `manual_template_baseline` | 0.24 | 4 | 38 |
| `llm_no_rag_baseline` | 0.72 | 4 | 14 |
| `agent_rag_tool_use` | 1.00 | 0 | 0 |

This is controlled pre-pilot evidence. It supports a pilot conversation because
the system handles scenario variety, source boundaries, tool/failure cases, and
human review gates. It does not prove production lift.

## Failure-Mode Replay

| Metric | Value |
|---|---:|
| Failure case count | 7 |
| Outbound confirmed count | 0 |
| Human review created count | 7 |
| Audit trail preserved count | 7 |
| Lead dropped count | 0 |
| Autonomous send allowed count | 0 |

Failure cases include provider timeout, provider hard failure, CRM write
failure, CRM lookup unavailable, duplicate detection, and missing tenant policy.

## Buyer Conversation Claim

Allowed claim:

> We do not have live production proof yet. We have controlled pre-pilot proof:
> 50 realistic garage-door scenarios, baseline comparison, failure-mode replay,
> zero autonomous sends, and a human-approval workflow ready for shadow-mode
> pilot review.

Blocked claims:

- Production ROI is proven.
- Conversion lift is proven.
- Live-client production results exist.
- Autonomous-send safety is proven.
- Paid production readiness is proven.

## Real Pilot Proof Still Needed

- De-identified real pilot transcripts.
- Operator edits and reject reasons.
- Provider failure/retry cases from real integrations.
- Human approval metadata.
- Booked-job attribution and baseline period metrics.
