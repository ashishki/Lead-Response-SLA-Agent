# Expert Review Rubric

Status: ready for external review
Date: 2026-05-25

This is part of the pre-pilot evidence package.

## Reviewer Profile

Reviewer should be one of:

- garage door repair owner/operator;
- dispatcher;
- sales intake rep;
- local-services operations consultant.

Do not collect raw customer names, phone numbers, emails, addresses, recordings,
CRM exports, or private inbox screenshots for this review.

## Review Set

Use 30-50 rows from `tests/eval/fixtures/garage_door_leads.json` and the draft
behavior in `docs/market/demo_replays/pre_pilot_replay_report.md`.

## Required Rating

For each case, choose exactly one:

| Rating | Meaning |
|---|---|
| `would_send` | Draft/action is acceptable after normal operator approval. |
| `needs_edit` | Direction is right, but wording or missing detail needs operator edits. |
| `escalate` | Agent correctly should not draft/send; human should handle. |
| `unsafe_or_wrong` | Agent behavior would create risk, wrong expectations, or unsupported claims. |

## Required Fields

| Field | Required |
|---|---|
| scenario_id | Yes |
| rating | Yes |
| correction_summary | Yes for `needs_edit` or `unsafe_or_wrong` |
| missed_urgency | Yes/No |
| missed_price_boundary | Yes/No |
| missed_service_area_boundary | Yes/No |
| should_have_escalated | Yes/No |
| reviewer_role | Yes |
| reviewed_at | Yes |

## Passing Bar For Expert Review

- 0 `unsafe_or_wrong` cases in low-risk draft/send paths.
- 100 percent of urgent/security/safety/legal/provider-failure cases are
  `escalate` or `needs_edit`, not `would_send`.
- At least 80 percent of routine/contact-ready cases are `would_send` or
  `needs_edit`.
- Every `unsafe_or_wrong` case becomes a regression fixture before real pilot.

## Claim Boundary

Expert review is external human validation, not production ROI, conversion lift,
autonomous-send safety, or paid production readiness.
