# Garage Door Repair Public Demo Report

Status: demo-ready for manual conversations
Date: 2026-05-23
Vertical: DFW emergency garage door repair
Data classification: public-source and synthetic demo data only

This report packages the public garage-door showcase for founder-led manual
conversations. It is not a case study, pilot result, ROI proof, conversion lift
claim, autonomous-send safety claim, or paid production readiness claim.

## Artifact Map

| Artifact | Location | Role |
|---|---|---|
| Public research protocol | `docs/market/open_source_research_protocol.md` | Source and claim boundary rules. |
| Source register | `docs/market/public_corpus/garage_door_repair_source_register.md` | 35 public records with source URLs, limitations, demo use, and PII handling. |
| Public seed corpus | `seed/verticals/garage_door_repair/public_corpus.json` | Seven public knowledge slices for demo-pack work. |
| Knowledge pack | `seed/verticals/garage_door_repair/corpus.json` | Approved demo knowledge documents, including public-source entries with source IDs and URLs. |
| Scenario bank | `tests/eval/fixtures/garage_door_leads.json` and `docs/market/public_corpus/garage_door_scenario_bank.md` | 50 synthetic inbound lead scenarios. |
| Replay artifacts | `docs/market/demo_replays/garage_door_replay_report.json` and `docs/market/demo_replays/garage_door_replay_report.md` | Deterministic replay output with human approval enabled. |

## Vertical Corpus Summary

- 35 public source records were captured from DFW provider pages, provider
  service pages, public cost guides, and public safety/manual guidance.
- Seven public knowledge slices are available: service area, emergency claims,
  repair taxonomy, pricing boundary, booking intake, safety boundary, and
  commercial escalation.
- Knowledge-pack entries cite source record IDs and URLs, or explicitly mark
  assumptions. They do not include private lead logs, CRM exports, call
  recordings, inboxes, paid lead portals, copied reviews, or scraped personal
  data.
- Public evidence supports demo behavior only. Tenant-specific service area,
  exact pricing, final booking policy, warranty policy, and commercial quoting
  still require approved tenant knowledge.

## Scenario Coverage

The synthetic scenario bank contains 30 demo leads:

| Coverage area | Count / examples |
|---|---|
| Routine repair | opener, panel, sensor, roller, noisy-door, tune-up cases. |
| Urgent repair | stuck-open, vehicle-trapped, off-track, crooked, will-not-close cases. |
| Missing-field intake | missing city, issue, contact channel, or urgency. |
| Supported questions | service area, after-hours fee caveat, appointment confirmation, broad pricing range. |
| Unsupported/risky cases | out-of-area, exact final price, DIY spring/cable repair, refund, safety advice. |
| Commercial/high-value | warehouse dock doors, roll-up doors, multi-door property work. |
| Booking boundary | booking without explicit acceptance is blocked. |

Every scenario cites `GD-PUB-*` source IDs or an explicit assumption and records
expected extracted fields, next action, handoff reason, and unsafe/unsupported
expectation.

## Replay Metrics

The deterministic replay harness generated 30 replays from the synthetic lead
fixture with human approval enabled:

| Metric | Result |
|---|---|
| Scenario count | 50 |
| Handoff count | 15 |
| Unsafe/unsupported count | 20 |
| Unsafe autonomous send count | 0 |
| Autonomous send enabled | no |
| Provider adapters called | no |

Each replay includes transcript, extracted fields, proposed-reply field,
evidence IDs, handoff reason, and send/no-send decision. Safe drafts require
operator approval. Unsafe, unsupported, high-value, booking-without-acceptance,
and low-confidence cases do not produce autonomous sends.

## Demo Examples

| Scenario | What the demo shows | Boundary |
|---|---|---|
| Vehicle trapped in Fort Worth | Urgent lead extraction and human handoff. | No exact arrival promise. |
| Keller service-area question | Evidence-grounded service-area answer candidate. | Future tenant coverage must be approved. |
| Exact spring price request | Human-review routing for pricing commitment. | No exact final quote before diagnosis. |
| DIY torsion spring request | No customer-facing repair instructions. | Safety advice routes to human review. |
| Warehouse dock doors down | Commercial/high-value escalation. | No commercial quote or booking without owner/operator review. |
| Booking without accepted window | Booking blocked until explicit acceptance. | No tool execution without fresh offer and acceptance. |

## Safety Boundaries

- Human approval remains enabled for every demo replay.
- Public-source data cannot justify autonomous customer sends.
- Exact final pricing, warranty/refund decisions, DIY spring or cable repair,
  commercial quotes, high-value multi-door work, and out-of-area promises route
  to human review.
- Demo artifacts contain no real customer names, phone numbers, emails,
  addresses, transcript text, CRM exports, or paid lead portal data.
- Claims about response-time improvement, booked jobs, revenue recovery, ROI,
  buyer willingness to pay, or paid readiness require real pilot evidence.

## Missing Real-Pilot Evidence

The public demo does not yet prove:

- live inbound lead volume or channel mix;
- baseline first-response time from the buyer's real leads;
- booked-job attribution or recovery of missed leads;
- dispatcher/operator review workload in production;
- buyer willingness to pay;
- provider delivery behavior under real email, WhatsApp, Telegram, calendar, or
  CRM traffic;
- tenant-approved service-area, pricing, booking, warranty, refund, and
  commercial escalation policies;
- privacy/legal acceptance for customer-facing terms.

## Real Pilot Proof Plan

A real pilot must prove the following before any stronger claim:

| Claim area | Required proof |
|---|---|
| Response-time improvement | Approved lead source timestamps comparing baseline and pilot first-response p50/p95. |
| Booking or recovery impact | Buyer-confirmed booked jobs, qualified handoffs, and attribution rules. |
| ROI or paid readiness | Buyer-approved cost, job value, payment decision, and operator review workload. |
| Autonomous-send safety | Human-approved replay history, no unsafe sends, and explicit approval to widen send authority. |
| Production reliability | Provider reconciliation, alert routing, rollback drill, and incident process under real traffic. |
| Legal/privacy readiness | Human-approved privacy, retention, terms, and subprocessor wording. |

## Conversation Use

Use this report to ask for a narrow replay or pilot conversation:

"This is a public-source demo, not a case study. It shows the workflow we would
run against your approved lead source: fast acknowledgement, field collection,
evidence-grounded answers, and human review for risky cases. The next proof step
is measuring your real response times, review workload, and booked outcomes."
