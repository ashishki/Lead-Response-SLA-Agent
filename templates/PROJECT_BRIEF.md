# Project Brief: Lead Response SLA Agent

Use this document before running `prompts/STRATEGIST.md`. The goal is not to pre-design the system, but to give the Strategist enough context to choose the right solution shape, governance level, runtime tier, and model strategy without guessing.

---

## 1. Project

- **Project name:** Lead Response SLA Agent
- **One-sentence summary:** An AI-assisted lead-response system that contacts inbound leads within seconds, qualifies them, books the next step, and escalates risky or high-value cases to a human operator.
- **Why this project exists:** Many service businesses lose high-intent leads because nobody responds quickly enough. The `@its_capitan` research highlighted a narrow AI appointment-setter case where contacting a lead within seconds rather than minutes materially improved conversion. This project turns that pattern into a guarded, measurable workflow automation product.
- **What success looks like in v1:** For one selected vertical, the system receives inbound leads from a form or webhook, sends the first response within 30 seconds, asks 2-4 qualifying questions, records structured lead data, offers a booking slot, and provides an operator dashboard with transcripts, overrides, latency metrics, and conversion outcomes.

## 1b. Problem Fit and Adoption Reality

Answer these before describing the desired architecture. The Strategist uses
this section to avoid designing a polished AI system around an unproven or
demo-only need.

- **Concrete operational pain:** Leads arrive through forms, Telegram, WhatsApp, email, or landing pages, but humans respond late, inconsistently, or without enough context. In time-sensitive categories, a delay of a few minutes can send the customer to a competitor.
- **Current workaround:** Manual inbox monitoring, CRM notifications, simple autoresponders, missed-call callbacks, template replies, or sales reps checking forms during business hours.
- **Why existing process is insufficient:** Static autoresponders do not qualify the lead, cannot answer basic context-specific questions, do not book a slot, and do not create structured CRM data. Fully manual response is slow and inconsistent. Unguarded AI chatbots can hallucinate prices, availability, policy, legal, or medical claims.
- **First user / buyer / operator who feels the pain:** A small service business owner or operations lead in a time-sensitive vertical such as car rental, clinic intake, real estate, education admissions, legal intake, or home services. First internal operator is the AI engineer configuring and monitoring one pilot workflow.
- **What would make v1 not worth adopting:** If setup takes longer than manual process improvement, if the agent gives unsafe answers, if it cannot integrate with the existing intake source, if it does not reduce response latency, or if operators do not trust the transcript and audit trail.
- **Adoption proof metric:** p95 first-response latency below 30 seconds, at least 80 percent of inbound leads captured as structured records, and measurable improvement in booked calls or qualified-lead handoff versus the previous baseline.
- **Claims that are out of bounds before evidence:** "Replaces sales reps", "fully autonomous closer", "guarantees conversion lift", "handles regulated advice", "production-ready for every vertical", "zero-touch customer support".
- **Work AI will not replace:** Final sales judgment, pricing exceptions, refunds, legal/medical/financial advice, dispute handling, high-value commitments, and accountability for customer promises.

## 2. Users and Workflows

- **Primary users / operators:** Business owner, sales/ops manager, intake coordinator, support/lead-response team, and AI engineer/operator maintaining the workflow.
- **Main workflow 1:** A lead arrives from a form, webhook, Telegram/WhatsApp message, or email. The system acknowledges quickly, extracts intent and contact fields, and starts a constrained qualification flow.
- **Main workflow 2:** The agent asks targeted follow-up questions, answers only from the approved knowledge base, proposes a booking slot or handoff, and escalates when confidence or policy boundaries require a human.
- **Main workflow 3:** Operators review transcripts, approve or correct escalated responses, tag outcomes, and use the feedback to improve prompts, guardrails, knowledge base entries, and eval cases.

## 3. Scope

- **In scope for v1:** One vertical, one or two intake channels, one calendar/booking integration, one CRM or spreadsheet destination, structured lead extraction, SLA timers, transcript storage, approval/escalation queue, eval cases, and basic observability.
- **Out of scope / non-goals:** Multi-vertical marketplace, fully autonomous sales closing, outbound cold outreach, payment collection, complex CRM automation, omnichannel contact center replacement, voice calls, and regulated-domain advice.

## 4. AI Scope

- **Where AI may be needed:** Understanding messy lead messages, classifying intent, extracting structured fields, drafting replies, choosing the next qualifying question, summarizing the conversation, and checking whether the lead is ready for human handoff.
- **Where AI is explicitly not wanted:** Webhook verification, authentication, tenant/role checks, SLA timers, calendar slot rules, rate limits, budget limits, retry logic, audit logging, message idempotency, and hard escalation policies.
- **Possible retrieval / RAG need:** Yes. The agent needs retrieval over approved business knowledge: service descriptions, pricing ranges, availability rules, location/service-area rules, cancellation policies, FAQs, and escalation instructions.
- **If retrieval is needed, is text-only likely sufficient or is multimodal evidence truly required:** Text-only is sufficient for v1. The system can run on FAQs, policies, price sheets, CRM fields, and booking rules.
- **If multimodal may be needed, which modalities and why:** Later versions may ingest screenshots, documents, or photos if the vertical requires them, for example property photos, insurance documents, or medical intake attachments. This is not required for v1.
- **Possible tool-use need:** Yes. Tools may read/write CRM records, create calendar bookings, send Telegram/WhatsApp/email messages, fetch available slots, look up lead history, and create human-review tasks.
- **Possible planning / agentic behavior need:** Limited and state-machine constrained. The agent can choose the next step within a fixed conversation policy, but it should not improvise promises, discounts, legal statements, or final sales commitments.

## 5. Deterministic Candidates

List the parts that probably should stay deterministic unless the Strategist proves otherwise.

- **Validation / policy checks:** Required fields, phone/email validation, webhook signature checks, tenant ownership, blocked topics, confidence thresholds, escalation triggers, and forbidden claims.
- **Routing / decision rules:** Which leads are auto-acknowledged, which require human review, which channel to reply on, booking eligibility, priority levels, and SLA breach alerts.
- **Calculations / transformations:** Latency metrics, lead age, SLA status, calendar availability windows, budget usage, per-channel conversion metrics, and structured field normalization.
- **Retries / idempotency / audit triggers:** Message send retries, duplicate lead detection, idempotency keys per inbound event, transcript append-only logs, human override records, and model-call cost logs.

## 6. Human Approval Boundaries

- **What actions must require human approval:** Non-standard pricing, discounts, refunds, legal/medical/financial advice, complaints, angry customers, high-value enterprise leads, uncertain availability, custom contract terms, and any response below the confidence threshold.
- **What can be automated safely:** First acknowledgement, basic qualification questions, FAQ answers grounded in approved knowledge, booking-slot suggestions, structured lead creation, reminders to operators, and conversation summaries.
- **Why these boundaries matter:** Fast response improves conversion only if the system does not create liability or false expectations. The product value is speed plus guardrails, not unrestricted autonomy.

## 7. Risk and Error Cost

- **What is expensive if the system is wrong:** It may promise unavailable inventory, quote wrong prices, mishandle sensitive data, damage customer trust, or create legal/compliance exposure.
- **What is expensive if the system is slow:** The lead may choose a competitor before the business responds, making latency a core product metric.
- **What is expensive if the system is inconsistent / variable:** Operators lose trust, customers get different answers for the same policy, and eval baselines become impossible to maintain.
- **Blast radius if it fails badly:** Medium. A bad response can lose revenue or create a customer complaint. In regulated verticals the blast radius can become high, so v1 should avoid regulated advice.
- **Audit / explainability needs:** High. Every outbound message must be traceable to inbound text, retrieved knowledge, policy checks, model output, and any human approval/override.

## 8. Data

- **Primary data sources:** Inbound lead messages, website form payloads, chat transcripts, approved FAQ/knowledge-base documents, service/pricing rules, calendar availability, CRM lead records, and operator feedback.
- **Approximate data volume:** v1 pilot may handle tens to hundreds of leads per month. Architecture should tolerate thousands per month without redesign.
- **Does data change frequently:** Yes. Pricing, availability, service areas, FAQ answers, staff schedules, and lead status can change daily.
- **Sensitive / regulated data present:** Yes. Names, phone numbers, emails, chat content, booking details, and possibly sensitive context depending on vertical. Avoid medical/legal/financial advice in v1.
- **Retention / deletion expectations:** Keep transcripts and audit records long enough for business review and eval improvement. Support manual deletion/export for lead records and redact secrets from logs.

## 8b. Continuity and Evidence

- **Which decisions are likely to be revisited later:** Escalation rules, prompt revisions, knowledge-base updates, vertical choice, pricing-answer policy, and whether a lead was qualified correctly.
- **What prior evidence or proof will future agents need to find quickly:** Conversation transcripts, retrieved knowledge snippets, model outputs, human corrections, lead outcomes, SLA metrics, and eval cases tied to real failures.
- **Will work span multiple sessions / agents / weeks:** Yes. The project will need iterative rollout, prompt/eval tuning, policy updates, and feedback from operators.
- **Any existing docs, ADRs, audits, or notes that should become retrieval anchors:** `gdev-agent` patterns for webhooks, HITL approval, tenant boundaries, evals, and observability; `telegram-research-agent` evidence-memory patterns; and the `@its_capitan` appointment-setter source case (`https://t.me/its_capitan/437`).

## 9. Integrations

- **External APIs / services:** Website forms/webhooks, Telegram Bot API, WhatsApp provider such as Twilio or 360dialog, email provider, Google Calendar or Calendly, CRM/spreadsheet target such as HubSpot, Airtable, Google Sheets, or a simple internal dashboard.
- **Databases / storage:** PostgreSQL for production-style v1, with tenant-safe schema if multi-client; Redis for queues/SLA timers if needed; object/file storage for knowledge-base uploads if used.
- **Auth / identity provider:** Operator login for dashboard; JWT/RBAC if multi-tenant. For internal pilot, a single admin account may be enough.
- **Webhooks / messaging / queues:** Required. Inbound webhook receiver, outbound messaging queue, retry queue, SLA timeout jobs, and event log.

## 10. Constraints

- **Preferred stack:** Python, FastAPI, Pydantic, PostgreSQL, Redis, Docker, structured logging, LLM structured outputs/tool use, and a small operator UI or Telegram-first admin workflow.
- **Deployment target:** VPS or containerized deployment. systemd is acceptable for first pilot; Docker Compose is preferred when adding queue/DB services.
- **Budget constraints:** Medium. Model calls should be controlled with cheap extraction/classification first and stronger models only for reply drafting or ambiguous cases.
- **Latency / throughput expectations:** First deterministic acknowledgement under 2 seconds where possible. Full AI-assisted first response under 30 seconds p95. Throughput for v1 can be modest but must handle bursts.
- **Compliance requirements:** Avoid regulated advice in v1. Treat PII carefully, log minimally, redact secrets, and maintain audit records for outbound messages.
- **Network / security restrictions:** Verify inbound webhooks, keep tokens in environment/secrets, enforce outbound provider rate limits, and isolate tenant/customer data if multi-tenant.

## 11. Runtime and Operations

- **Should runtime stay simple (managed service / container) if possible:** Yes. Start with one deployable service plus database; add Redis/worker only when SLA timers and retries justify it.
- **Any need for shell, package, or toolchain mutation at runtime:** No. Runtime should not mutate its own toolchain.
- **Any need for privileged actions or long-lived isolated workers:** No privileged workers. Long-lived workers may be useful for messaging queues and SLA timers but should run with least privilege.
- **Recovery / rollback expectations:** Inbound events must be idempotent. Outbound messages need send status. Failed model calls should degrade to safe human handoff. Rollback should not lose transcripts or lead records.

## 12. Model and Cost Expectations

Only fill what you know. The Strategist should still make the final recommendation.

- **Cost sensitivity:** medium
- **Latency sensitivity:** high for first response; medium for post-conversation summaries and analytics
- **Expected request / task volume:** Pilot volume is tens to hundreds of leads per month; each lead may require 2-6 model-assisted turns.
- **If AI is used, should the system prefer smaller / cheaper models by default:** Yes for extraction, routing, and summarization. Use stronger models for final customer-facing replies when needed.
- **Any required capabilities:** Structured output, function calling/tool use, retrieval-grounded answering, low-latency response drafting, conversation summarization, and confidence scoring.
- **Preview-model tolerance:** low. Customer-facing replies should use stable models with regression tests.

## 13. Success Metrics

- **Business success metric:** Increase in qualified calls/bookings or sales-ready handoffs versus baseline.
- **Quality metric:** Percentage of conversations that pass eval checks for correctness, policy compliance, and useful next-step capture; human override rate by category.
- **Latency metric:** p95 first-response latency below 30 seconds; deterministic acknowledgement under 2 seconds where applicable.
- **Cost metric:** Average model and messaging cost per qualified lead stays below a configured target, tracked per channel/tenant.
- **Operational metric:** SLA breach rate, escalation rate, duplicate lead rate, failed send rate, booking completion rate, and number of real failure cases added to evals.

---

## Usage

1. Send this completed brief to the Strategist.
2. Let the Strategist ask one batch of clarifying questions.
3. Use the resulting architecture package as the Phase 1 input to the rest of the playbook.
