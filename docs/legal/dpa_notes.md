# DPA Notes And Contract Boundary

Status: pre-pilot contract template; no live customer agreement or deployment
Date: 2026-05-23

These notes are not a standalone legal agreement and have not been exercised
with a live customer. They define implementation-level boundaries that would
require legal, provider, security, and operator review before any paid pilot.

## Roles

- Customer is the controller or business owner of lead and customer data.
- Lead Response SLA Agent operates as processor/service provider for configured
  inbound, response, review, booking, CRM, and reporting workflows.
- The founder/operator administers the first pilot and must follow the runbook
  privacy, retention, export, delete, support, and incident procedures.

## Supported Commitments

| Topic | Supported commitment |
|---|---|
| Purpose limitation | Use customer data only to process inbound leads, draft/review responses, route handoffs, write approved provider records, measure pilot outcomes, and operate the service. |
| Tenant isolation | Tenant-scoped data access requires tenant context and authenticated operator/owner roles. |
| Human approval | Unsafe, unsupported, exact-pricing, booking-without-acceptance, refund, complaint, commercial/high-value, and safety advice cases stay in human review. |
| Export | Provide tenant-scoped export using `tenant-export-v1` and the documented PII field map. |
| Delete/anonymize | Use v1 anonymization for customer delete requests and record `tenant_data_anonymized`. |
| Retention | Apply configured tenant retention policy; default pilot retention is 90 days unless the order form sets a shorter value. |
| Audit | Preserve audit events for approvals, config changes, provider sends, export/delete, retention, and release-impacting operator actions. |
| Security incident handling | Use PII-free incident notes and customer templates; preserve audit records and stop affected workflows when needed. |

## Unsupported Or Not Yet Promised

- hard deletion of all database rows;
- zero-retention operation;
- SOC 2, ISO 27001, HIPAA, GDPR certification, or regulated-advice coverage;
- autonomous outbound sends without human approval;
- cold outreach by WhatsApp, Telegram, SMS, email, or product agent;
- broad paid production readiness before real pilot evidence and legal review;
- customer-facing subprocessor promises beyond the enabled provider list.

## Required Order Form Inputs

Before a paid pilot starts, the order form must name:

- tenant name and operator contact;
- enabled inbound source and outbound channel;
- enabled subprocessors/providers;
- retention period and mode;
- export recipient and approval workflow;
- delete/anonymize requester approval path;
- support contact and incident notification path;
- human-review categories that must always remain manual;
- baseline and pilot measurement dates.

## Subprocessor Change Procedure

1. Identify the new provider and data categories it will receive.
2. Confirm the provider is required for the pilot workflow.
3. Update `docs/legal/privacy.md`, this file, deployment secrets, and runbook
   setup notes before enabling it.
4. Notify the pilot buyer through the agreed support channel before customer
   data flows to the new provider.
5. Run provider contract tests with fake responses or sandbox credentials.

## Evidence Links

- Export/delete/anonymize behavior: `tests/integration/test_data_export_delete.py`
- Retention enforcement behavior: `tests/integration/test_data_retention.py`
- Privacy docs checks: `tests/unit/test_privacy_docs.py`
- Runbook procedure: `docs/runbook.md#data-retention-export-and-delete`
