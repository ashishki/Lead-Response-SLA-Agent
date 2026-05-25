# Solo Showcase Readiness Review

Date: 2026-05-23
Reviewer: Codex verification pass (not independent)
Scope: Phase 22 T70-T77 public garage-door showcase artifacts

## Result

SOLO_SHOWCASE_READINESS_REVIEW: PASS

The public garage-door showcase is ready for founder-led manual conversations
and narrow replay/pilot discovery. It is not ready for autonomous send, paid
production launch, conversion-lift claims, ROI claims, or customer-facing legal
terms.

## Evidence

| Artifact | Location | Status |
|---|---|---|
| Public research protocol | `docs/market/open_source_research_protocol.md` | Complete |
| Public source register | `docs/market/public_corpus/garage_door_repair_source_register.md` | 35 public records |
| Public corpus seed | `seed/verticals/garage_door_repair/public_corpus.json` | 7 public knowledge slices |
| Knowledge pack | `seed/verticals/garage_door_repair/corpus.json` | Source-cited public entries added |
| Retrieval eval | `seed/verticals/garage_door_repair/retrieval_eval.json`, `docs/retrieval_eval.md` | Supported and unsupported public questions covered |
| Scenario bank | `tests/eval/fixtures/garage_door_leads.json`, `docs/market/public_corpus/garage_door_scenario_bank.md` | 50 synthetic demo scenarios |
| Replay artifacts | `docs/market/demo_replays/garage_door_replay_report.json`, `docs/market/demo_replays/garage_door_replay_report.md` | 30 replays, zero unsafe autonomous sends |
| Demo report | `docs/market/demo_report_garage_door_repair.md` | Ready for manual conversations |
| First-10 target list | `docs/market/first_10_targets.md` | Manual outreach only |

## Verification

| Check | Result |
|---|---|
| `DATABASE_URL=postgresql+asyncpg://lead_test:lead_test@localhost:55432/lead_sla_test REDIS_URL=redis://localhost:6380/0 .venv/bin/python -m pytest tests/ --tb=short` | 241 passed, 26 skipped |
| `.venv/bin/ruff check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` | passed |
| `.venv/bin/ruff format --check src/lead_sla_agent tests alembic scripts/onboard_tenant.py scripts/reset_demo_tenant.py scripts/smoke_test.py scripts/rollback_check.py scripts/replay_demo_leads.py` | passed |

## Acceptance Coverage

- T70 Public research protocol: allowed sources, forbidden sources,
  source-register fields, and blocked public-demo claims are documented and
  linked from market/demo docs.
- T71 Public source register: 35 public garage-door records are captured with
  URL/locator, captured_at, source type, evidence kind, extracted fact, demo
  use, limitation, and PII handling.
- T72/T67a Scenario bank: 50 synthetic scenarios cite public source IDs or explicit
  assumptions and include expected extraction, next action, handoff reason, and
  unsafe/unsupported expectation.
- T73 Knowledge pack and retrieval eval: public entries cite source IDs/URLs;
  unsupported public claims route to insufficient evidence or human review.
- T74 Replay harness: deterministic replays include transcript, extracted
  fields, proposed-reply field, evidence IDs, handoff reason, and send/no-send
  decision with human approval enabled.
- T75 Demo report: report includes corpus summary, scenario coverage, replay
  metrics, examples, safety boundaries, missing real-pilot evidence, and pilot
  proof plan.
- T76 First-10 list: each target cites public pages/source IDs and asks for a
  narrow manual replay/pilot conversation; automated outreach is forbidden.

## Decision

Ready for manual conversations:

- The founder can show the public demo report and replay artifacts.
- Outreach can start with the first-10 target list.
- The ask should be a 10-minute replay review or a narrow pilot-readiness
  conversation.

Not ready for:

- customer-facing ROI or conversion claims;
- paid production commitments;
- autonomous-send claims or expanded send authority;
- accepting real lead logs without privacy/legal approval;
- publishing customer-facing privacy, retention, or subprocessor terms.

## No-Go Conditions

Do not proceed to live customer data, paid launch, or autonomous-send expansion
if any of the following are true:

- T64 privacy/legal wording remains unapproved.
- A buyer cannot approve service-area, pricing, booking, warranty, refund, and
  escalation boundaries.
- The buyer cannot provide baseline response-time and outcome labels.
- The workflow would need automated outreach to get meetings.
- The demo is being used to imply conversion lift, ROI, or paid production
  readiness.
- Provider alerting, reconciliation, rollback, or incident process evidence is
  missing for the chosen pilot channel.

## Missing Real-Pilot Evidence

- real lead volume and channel mix;
- baseline first-response p50/p95;
- booked-job attribution and lost-lead recovery;
- operator review minutes and approval quality;
- buyer willingness to pay;
- provider delivery and reconciliation under real traffic;
- tenant-approved policies and legal/privacy terms.

## Next State

Phase 22 is complete. The next non-Codex step is founder-led manual outreach
using `docs/market/first_10_targets.md` and
`docs/market/demo_report_garage_door_repair.md`.

Codex should not resume T64 until the human approves privacy/legal wording,
retention promises, and subprocessor commitments for customer-facing terms.
