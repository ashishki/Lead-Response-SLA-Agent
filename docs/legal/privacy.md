# Privacy And Customer Data Handling

Status: pilot-ready draft
Date: 2026-05-23
Audience: pilot buyer and operator review

This document describes what the current product can technically support. It is
not a broad legal promise and should be attached to a paid pilot only after the
buyer-specific order form confirms the same limits.

## Data We Collect

| Data category | Examples | Why it is used |
|---|---|---|
| Tenant account data | tenant ID, operator role, configuration, approved channels | operate tenant-scoped access, routing, and settings |
| Lead contact data | customer name, phone, email, service city or ZIP | respond to inbound leads and qualify service requests |
| Conversation data | inbound message refs, outbound draft refs, transcript previews | preserve the review trail and first-response SLA evidence |
| Review data | human-review tasks, approvals, edits, no-send reasons | enforce human approval and improve safety |
| Provider metadata | provider, channel, delivery status, latency, failure reason, idempotency key hash | reconcile sends and debug delivery without exposing message text |
| Knowledge data | approved FAQs, service area, pricing ranges, booking rules, escalation policy | ground answers and route unsupported questions to review |
| Operational audit data | actor refs, action, resource refs, policy version, result, timestamp, PII-free metadata | prove approvals, exports, retention, and configuration changes |
| Usage data | counts of leads, AI-assisted replies, provider sends, review tasks, bookings, active channels | produce billing and pilot measurement exports without raw PII |

Raw webhook payloads are not retained as customer records. Logs, metrics, spans,
reports, and support notes must not include raw names, phone numbers, emails,
addresses, message text, transcript text, provider user IDs, provider message
IDs, tokens, or secrets.

## Retention

Default pilot retention is 90 days unless the signed tenant agreement sets a
shorter value. The supported v1 deletion mode is anonymization. Anonymization
removes direct customer identifiers while preserving operational counts,
tenant-scoped audit integrity, and aggregate reporting.

Retention enforcement covers:

- leads and contact fields;
- conversations and outcomes;
- transcripts and provider message IDs;
- review-task payloads;
- audit event metadata, scrubbed in place while preserving append-only event
  records;
- export artifacts, which are expired by clearing storage references and
  download URLs.

Docker container logs have a separate 14-day local retention target and must be
exported only for incidents after PII review.

## Export

Tenant export schema version: `tenant-export-v1`.

A tenant export includes leads, conversations, transcripts, audit events,
outcomes, review tasks, export records, retention policy, and a PII-field map.
Exports are tenant-scoped and must be reviewed for PII before sharing outside
the operating team.

## Delete And Anonymize

Customer delete requests use tenant anonymization in v1. The operation:

1. verifies requester authorization;
2. optionally exports tenant data first if the contract or customer request
   requires it;
3. redacts lead contact name, email, and phone;
4. removes transcript provider message IDs and redacts previews;
5. scrubs review payloads;
6. records a `tenant_data_anonymized` audit event with actor ID, reason,
   retention policy, and affected row counts.

Hard deletion is not promised in v1 unless a separate signed agreement and
implementation plan explicitly replace the anonymization mode.

## Subprocessors And Infrastructure

Current production-design subprocessors are limited to the services required for
the selected deployment and configured providers:

| Subprocessor category | Purpose | Notes |
|---|---|---|
| VPS host | run API, worker, PostgreSQL, Redis, and backups | selected deployment target for the first pilot |
| PostgreSQL | canonical tenant data store | tenant isolation uses tenant context and RLS-backed tables |
| Redis | queue, timer, retry, and cache state | ephemeral; not canonical customer record storage |
| Grafana Cloud or Prometheus-compatible metrics stack | alerting and metrics | metrics labels must be PII-free |
| Email provider | approved outbound email channel | only after sender/domain and operator approval |
| Twilio WhatsApp | approved WhatsApp channel | only with opt-in and operator approval |
| Telegram Bot API | approved Telegram channel | only when the user initiates or provides chat context |
| Calendar provider | slot lookup and booking after explicit acceptance | tests use fake provider responses |
| CRM provider | lead record destination | failed writes create audit/retry paths |
| OpenAI embedding API | production text embeddings when enabled | fake provider is used in normal tests |

Any pilot order form must list the exact enabled providers. Do not claim SOC 2,
HIPAA, GDPR certification, zero data retention, hard deletion, autonomous send,
or broad production readiness unless the system and contract have been updated
to support those promises.
