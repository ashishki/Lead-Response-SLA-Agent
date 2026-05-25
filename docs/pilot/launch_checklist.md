# First Pilot Tenant Launch Checklist

Status: launch-ready template
Date: 2026-05-23
Vertical: DFW emergency garage door repair

This checklist must be completed before routing real pilot traffic. It is a
launch control artifact, not a sales promise. Every outbound message remains in
human approval at launch.

## Pilot Identity

| Field | Value |
|---|---|
| Tenant name | TBD |
| Tenant slug | TBD |
| Buyer signer | TBD |
| Operator owner | TBD |
| Support contact | TBD |
| Inbound source | one approved source only |
| Outbound channel | one approved channel only |
| Launch date/time | TBD |
| Baseline period | 14 calendar days before launch |
| Pilot period | first 14 calendar days after launch |

## Pre-Launch Checklist

- Buyer signs off on success criteria and stop criteria before traffic is
  routed.
- Buyer approves service area, pricing-range language, booking rules, warranty
  boundaries, refund boundaries, safety boundaries, and commercial escalation.
- Buyer confirms baseline data sources: call tracking, website forms, outcome
  labels, and dispatch/review workload.
- Baseline metrics are captured before traffic is routed: response time p50/p95,
  missed lead rate, booked jobs, qualified handoffs, human-review workload, lead
  source mix, provider failure baseline, and unsafe automation baseline.
- Tenant knowledge corpus is uploaded from buyer-approved source documents.
- Retrieval eval passes for tenant knowledge and unsupported questions.
- Provider credentials are scoped to the selected channel and stored only in
  deployment secret storage.
- Operator accounts are created with least privilege and access review export is
  checked.
- Support contact and incident route are confirmed.
- Rollback/fallback owner is named.
- Human approval is enabled for every outbound message. Autonomous send remains
  disabled.

## Launch-Day Checklist

- Confirm `/health`, PostgreSQL, Redis, operator auth, provider sandbox, and
  unsafe-message handoff smoke checks pass.
- Confirm metrics and alert routing are live for first-response latency, queue
  depth, provider failure rate, API errors, SLA breaches, and unsafe automation
  blocks.
- Route only the approved inbound source to the pilot tenant.
- Send a test inbound event through the selected source.
- Confirm review task creation, transcript refs, evidence IDs, proposed reply,
  and no-send/approve controls.
- Confirm the first real outbound reply is manually approved by the operator.
- Confirm provider reconciliation records delivery status or failure reason.
- Record launch timestamp and first event ID/hash in the pilot log without raw
  customer PII.

## First-Week Checklist

- Review daily response time p50/p95, review queue age, provider failures, and
  unsafe automation blocks.
- Buyer or operator labels outcomes at least twice during the first week.
- Review all no-send, edited, unsupported, safety, pricing, booking, and
  commercial/high-value handoffs.
- Patch tenant knowledge only from buyer-approved text.
- Keep human approval enabled for every outbound message.
- Send weekly buyer update with response, booking, handoff, review workload,
  provider failure, and unsafe automation metrics.
- Stop or redesign if human-review rate remains above 50 percent, baseline data
  is unavailable, unsafe reply risk appears, or buyer cannot label outcomes.

## Rollback And Fallback Checklist

- Fallback: pause agent-initiated replies and route new leads to human review.
- Fallback: buyer resumes existing dispatch/answering-service workflow.
- Rollback: disable provider routing to the pilot tenant before app rollback if
  provider behavior is suspect.
- Rollback: run app rollback using `docs/runbook.md#rollback`.
- Data safety: preserve audit events and do not delete customer data during
  incident triage.
- Customer update: use support templates without raw customer PII.
- Restart only after smoke checks, provider reconciliation, and buyer approval
  pass.

## Buyer Signoff

| Signoff Item | Required Before Launch | Buyer Initials / Date |
|---|---|---|
| Success criteria accepted | yes | TBD |
| Stop criteria accepted | yes | TBD |
| Baseline metrics captured | yes | TBD |
| Human approval required for every outbound message | yes | TBD |
| Approved knowledge and unsafe categories accepted | yes | TBD |
| Support and incident contact accepted | yes | TBD |
| Rollback/fallback plan accepted | yes | TBD |

## Launch Decision

Launch is allowed only when every required signoff item is complete and the
operator confirms:

- no autonomous outbound send is enabled;
- baseline metrics are captured;
- success and stop criteria are signed off;
- provider sandbox and smoke checks pass;
- rollback/fallback path is ready.
