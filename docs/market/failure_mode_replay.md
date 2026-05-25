# Failure-Mode Replay

Status: generated summary
Date: 2026-05-25

Source artifact:
`docs/market/demo_replays/failure_mode_replay_report.json`

## Covered Failures

- SMS provider timeout.
- Email provider hard failure.
- CRM write failure.
- CRM lookup unavailable.
- Possible duplicate lead.
- Missing tenant policy.

## Result

| Metric | Value |
|---|---:|
| Failure case count | 7 |
| Outbound confirmed count | 0 |
| Human review created count | 7 |
| Audit trail preserved count | 7 |
| Lead dropped count | 0 |
| Autonomous send allowed count | 0 |

## Required Behavior

- Do not mark provider sends as confirmed after timeout or hard failure.
- Do not drop leads when CRM writes fail.
- Do not invent appointment, warranty, financing, or customer-status facts.
- Create human review for every failure case.
- Preserve audit visibility.
- Keep autonomous send disabled.

## Claim Boundary

Failure-mode replay is controlled pre-pilot evidence. Real provider outage
rates, retry behavior, and operational recovery must be measured in a live pilot.
It does not prove production ROI, conversion lift, autonomous-send safety, or
paid production readiness.
