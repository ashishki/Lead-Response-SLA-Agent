# Garage Door Repair Demo Script

Audience: DFW garage door repair owner/operator or dispatch manager
Goal: show missed-revenue recovery, not generic AI capability

Demo data rule: solo demo-pack work must follow
`docs/market/open_source_research_protocol.md`. Treat public-source examples and
generated leads as synthetic demo material; do not claim conversion lift, ROI,
autonomous-send safety, or paid production readiness until a real pilot proves
those outcomes.

## Opening

"You advertise same-day or emergency garage door repair. The product is built for the moments when a lead calls or fills a form while the dispatcher is busy, after hours, or a technician is on a job. The goal is to answer fast, collect the right details, and keep risky replies in human review."

## Demo Flow

1. New lead arrives from website form or callback request.
2. Agent acknowledges within the SLA and asks only for missing required fields: city/ZIP, issue type, urgency, stuck-open/stuck-closed status, vehicle trapped, and phone.
3. Lead asks a supported service-area question. Show answer grounded in approved garage door corpus.
4. Lead asks for an exact spring replacement price. Show human review because exact final pricing is not allowed.
5. Lead asks to book a slot but has not accepted the time. Show booking blocked until explicit acceptance.
6. Operator opens review queue, sees lead summary, transcript refs, evidence IDs, proposed reply, required action, and approves/edit/no-sends.
7. Weekly report shows response p50/p95, booked outcomes, qualified handoffs, review rate, provider failures, and unsafe automation count.

## Public Demo Report

Use `docs/market/demo_report_garage_door_repair.md` as the showable public demo
pack. State that it contains 35 public source records, 50 synthetic lead
scenarios, deterministic replay artifacts, and zero unsafe autonomous sends in
the demo replay. Do not present those artifacts as conversion lift, ROI,
autonomous-send safety, or paid production readiness evidence.

## Real Pilot Proof Ask

Ask for a narrow replay or pilot conversation that can prove baseline
first-response time, booked-job attribution, operator review workload,
provider reliability, and tenant-approved service/pricing/booking boundaries.

For first outreach, use `docs/market/first_10_targets.md`. Outreach is manual
only: no automated email, SMS, social, form-fill, robocall, scraping,
enrichment, or product-agent outreach.

## Talk Track

- "This does not replace your dispatcher. It handles fast first response and clean handoffs."
- "The agent only answers from approved policy text."
- "Exact pricing, DIY spring repair, complaints, commercial/high-value jobs, and uncertain bookings go to human review."
- "The weekly report is the payment conversation: did response time improve, did booked jobs increase, and did review work stay reasonable?"

## Close

"If we recovered three booked jobs in two weeks with zero unsafe replies, would that justify continuing at one of the pilot packages?"

## Demo Success Signal

The buyer asks about their own missed calls, lead sources, response times, booking attribution, or review workload. If the buyer only asks about the AI model, steer back to recovered jobs and dispatcher burden.
