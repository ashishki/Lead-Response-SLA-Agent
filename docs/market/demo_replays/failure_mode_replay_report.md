# Garage Door Failure-Mode Replay

Status: generated
Generated on: 2026-05-25
Data classification: synthetic failure replay

## Summary

- Failure case count: 7
- Outbound confirmed count: 0
- Human review created count: 7
- Audit trail preserved count: 7
- Lead dropped count: 0
- Autonomous send allowed count: 0

## Cases

| scenario_id | category | failure_simulation | expected_handoff_reason | human_review_created | audit_trail_preserved |
|---|---|---|---|---|---|
| gd-lead-033 | duplicate | possible_duplicate | possible_duplicate | True | True |
| gd-lead-039 | provider_failure | sms_provider_timeout | provider_timeout | True | True |
| gd-lead-040 | provider_failure | email_provider_hard_failure | provider_hard_failure | True | True |
| gd-lead-041 | crm_failure | crm_write_failure | crm_write_failure | True | True |
| gd-lead-042 | crm_failure | crm_lookup_unavailable | crm_lookup_unavailable | True | True |
| gd-lead-047 | tenant_policy_missing | missing_tenant_policy | missing_tenant_policy | True | True |
| gd-lead-048 | tenant_policy_missing | missing_tenant_policy | missing_tenant_policy | True | True |

## Claim Boundary

Failure-mode replay is controlled evidence only. Real provider failure rates and retry outcomes require a live pilot.
