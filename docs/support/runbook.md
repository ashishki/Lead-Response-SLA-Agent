# Support Runbook

Date: 2026-05-20
Scope: pilot customers for Lead Response SLA Agent

## Issue Intake

Accepted support channels for pilot customers:

- shared support email or founder/operator direct email
- agreed customer Slack/WhatsApp thread if included in pilot terms
- urgent phone call for Sev1 only

Every issue must record:

- tenant name or tenant hash
- reporter
- severity
- started_at
- affected channel or provider
- customer-visible impact
- current workaround
- owner
- next update time

Do not paste customer names, phone numbers, emails, raw message text, provider message IDs, or transcript text into support notes.

## Severity Levels

| Severity | Definition | First response | Update cadence | Examples |
|----------|------------|----------------|----------------|----------|
| Sev1 | Customer-facing outage, unsafe autonomous reply, data exposure, or all lead intake blocked | 15 minutes | every 30 minutes until mitigated | webhook rejects all valid leads, provider sends unsafe content, PII leak |
| Sev2 | Major degraded workflow with workaround | 1 business hour | every 4 business hours | provider send outage with human review fallback, queue backlog, stale retrieval index |
| Sev3 | Minor defect or reporting issue | 1 business day | every 2 business days | weekly report mismatch, non-critical analytics gap |
| Sev4 | Question, enhancement, or documentation request | 2 business days | weekly or by agreement | new FAQ request, copy change, extra user request |

## Escalation

| Trigger | Escalate to | Action |
|---------|-------------|--------|
| Unsafe autonomous reply | founder/operator owner immediately | pause autonomous replies for affected category and route to human review |
| Suspected data exposure | founder/operator owner immediately | stop affected workflow, preserve audit logs, start privacy review |
| Provider outage over 30 minutes | deployment/operator owner | enable fallback, notify customer, retry after recovery |
| Retrieval regression | AI/operator owner | freeze knowledge changes, run evals, route unsupported answers to review |
| Queue backlog threatening SLA | deployment/operator owner | scale worker or pause non-critical jobs |

## Response Expectations

- Acknowledge every Sev1/Sev2 with impact, workaround, owner, and next update time.
- Use PII-free identifiers in all updates.
- For Sev1 safety/data issues, customer update must not wait for root cause.
- Every Sev1 and every repeated Sev2 requires post-incident review.

## Post-Incident Review

Complete within 2 business days for Sev1 and within 5 business days for repeated Sev2.

Required sections:

- summary
- timeline
- customer impact
- detection source
- root cause
- mitigation
- prevention tasks
- owner and due date
- customer-facing follow-up

## Support Metrics

Track by tenant hash and severity:

- first response time
- time to mitigation
- time to resolution
- repeated incident count
- safety handoff count
- provider outage count

Support metrics must not include raw customer PII.
