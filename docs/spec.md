# Specification - Lead Response SLA Agent

Version: 1.0
Last updated: 2026-05-19
Status: Draft

---

## Overview

Lead Response SLA Agent gives one pilot service business a guarded, measurable workflow for responding to inbound leads quickly. The system accepts inbound events, acknowledges leads, qualifies them through a constrained AI-assisted conversation, answers only from approved text knowledge, writes structured lead records, proposes or books next steps through tools, and escalates unsafe or ambiguous cases to a human operator.

---

## User Roles

| Role | Permissions |
|------|-------------|
| Business owner / operations manager | Configure approved knowledge, review metrics, inspect transcripts, approve escalations, and adjust business rules. |
| Intake coordinator / sales operator | Review human-review queue, approve or edit risky replies, tag outcomes, and complete handoffs. |
| AI engineer / operator | Configure providers, monitor evals, inspect failures, update prompts/policies, and maintain deployment. |
| Lead / customer | Sends inbound questions and receives safe acknowledgement, qualification questions, grounded answers, or booking next steps. |

---

## Feature Area: Inbound Lead Intake

### Description

The system receives lead events from signed webhooks or configured messaging providers, normalizes them into a common event schema, deduplicates repeated delivery, and creates an append-only inbound event record.

### Acceptance Criteria

1. Valid signed webhook payloads are accepted with HTTP 202 and persisted with source event ID, tenant ID, channel, received timestamp, and raw payload hash.
2. Invalid webhook signatures return HTTP 401 and do not create inbound event, lead, conversation, or audit rows.
3. Replayed source event IDs return the existing normalized event ID and do not create duplicate lead or transcript rows.
4. The intake path emits no raw name, phone, email, or message body in logs, span attributes, metrics, or error responses.

### Out of Scope for v1

- Voice call ingestion.
- Browser chat widget implementation beyond webhook-compatible events.
- Multi-provider auto-discovery.

---

## Feature Area: Fast Acknowledgement and SLA Tracking

### Description

The system sends a deterministic acknowledgement where possible and tracks first-response latency, SLA breach status, and provider send outcomes.

### Acceptance Criteria

1. The system records first-response latency from inbound event timestamp to outbound send confirmation.
2. A safe acknowledgement can be sent without an LLM when required lead fields and channel permissions are present.
3. SLA breach records are created when the first response exceeds the configured threshold.
4. Provider send failures create retry jobs with bounded retry count and human-review fallback.

### Out of Scope for v1

- Sophisticated send-time optimization.
- Cross-channel conversation merging beyond explicit lead identifiers.

---

## Feature Area: Lead Qualification Conversation

### Description

The conversation runtime extracts structured lead fields, chooses the next allowed question or action inside a deterministic state machine, and stops when the lead is booked, qualified for handoff, unsupported, timed out, or over budget.

### Acceptance Criteria

1. Extraction produces a strict schema containing contact fields, intent, requested service, urgency, budget when provided, and missing required fields.
2. The runtime chooses only actions from the allowed policy set: acknowledge, ask question, answer with evidence, propose slot, create/update lead, book accepted slot, or handoff.
3. The loop terminates with a recorded reason when max turns, max tool calls, max model budget, unsupported topic, booking completion, or human-review condition is reached.
4. Every model output used for a customer-facing decision is stored with schema version, policy decision, and audit event ID.

### Out of Scope for v1

- Open-ended autonomous sales negotiation.
- Hidden model memory.
- Runtime subagents.

---

## Feature Area: Retrieval

### Description

The agent uses text-only retrieval over approved tenant knowledge to answer business FAQ and policy questions. Retrieval is not used for general web search. Unsupported questions must return `insufficient_evidence` and create a human-review task.

### Sources Indexed

- Approved FAQs.
- Service descriptions.
- Pricing ranges.
- Service-area rules.
- Cancellation policies.
- Booking rules.
- Escalation instructions.

### Query Types

- Price or package question.
- Availability or service-area question.
- Booking/cancellation policy question.
- Basic service description question.
- Unsupported legal, medical, financial, or custom-contract question.

### Citation / Evidence Format

Customer-facing text does not need expose citations in v1, but the audit trail must store evidence chunk IDs, source document IDs, source titles, and retrieval scores for every grounded answer.

### Retrieval Mode

Text-only. Multimodal retrieval is out of scope for v1.

### Acceptance Criteria

1. Ingestion stores chunks with tenant ID, source document ID, source title, effective date, index schema version, content hash, and embedding reference.
2. Query-time retrieval enforces tenant filtering before evidence is returned to the reply drafter.
3. Unsupported queries return `insufficient_evidence` and create a human-review task without generating a fabricated answer.
4. Retrieval eval tracks hit@3, citation precision, no-answer accuracy, and retrieval latency against a 10-query seed dataset.

### Out of Scope for v1

- Multimodal retrieval.
- Live web search.
- Cross-tenant corpus sharing.

---

## Feature Area: Tool-Use Integrations

### Description

The system exposes registered tools for outbound messaging, CRM/spreadsheet writes, calendar lookup/booking, lead-history lookup, and human-review task creation. Tool schemas are versioned, side effects are explicit, and unsafe actions require confirmation.

### Acceptance Criteria

1. Every tool schema includes name, version, input schema, output schema, side-effect classification, idempotency rule, timeout, retry policy, and human-gate rule.
2. Side-effecting tools reject calls without an idempotency key when an idempotency key is required by the tool catalog.
3. Calendar booking is allowed only after explicit customer acceptance and a fresh availability lookup.
4. Unsafe message sends create a human-review task instead of sending directly.

### Out of Scope for v1

- Payment collection.
- Full CRM workflow automation.
- Arbitrary external tool execution.

---

## Feature Area: Human Review and Operator Dashboard

### Description

Operators need a queue for escalated conversations, transcript inspection, approve/edit actions, outcome tagging, and feedback capture for eval improvement.

### Acceptance Criteria

1. Human-review tasks show lead summary, handoff reason, transcript, retrieved evidence IDs, proposed reply when available, and required approval action.
2. Operator approval records actor ID, timestamp, original draft, final message, and reason code.
3. Outcome labels can be attached to a lead and are queryable for conversion and eval analysis.
4. Operator endpoints enforce authentication and tenant/role authorization before returning lead or transcript data.

### Out of Scope for v1

- Rich analytics BI dashboard.
- Multi-role workflow approvals.
- Mobile-native operator app.

---

## Feature Area: Evaluation and Observability

### Description

The product must measure whether speed, grounding, side-effect safety, and bounded conversation behavior remain within acceptable limits.

### Acceptance Criteria

1. CI runs unit/integration tests, lint, format check, and active profile eval suites.
2. Retrieval eval detects regressions in hit@3, citation precision, no-answer accuracy, and latency.
3. Tool eval validates schema conformance, idempotency rejection, unsafe-action gating, and provider timeout handling.
4. Agent eval validates allowed action selection, termination reasons, turn budget enforcement, and handoff creation.
5. `GET /health` returns dependency health and retrieval freshness without leaking PII.

### Out of Scope for v1

- Automated prompt optimization.
- Production incident automation.
- Full load-testing gate before pilot traffic exists.
