# Pilot Vertical: DFW Emergency Garage Door Repair

Date: 2026-05-20
Status: selected hypothesis for founder-led validation

Solo demo-pack work for this vertical must follow the public research protocol
in `docs/market/open_source_research_protocol.md`. Public sources may shape the
knowledge pack, synthetic demo lead scenarios, demo report, and manual target
list. They must not be used to claim conversion lift, ROI,
autonomous-send safety, or paid production readiness.

## Selected Vertical

Lead Response SLA Agent will start with independent garage door repair companies in Dallas-Fort Worth that advertise same-day or 24/7 emergency repair.

Primary buyer: owner/operator or dispatch manager of a 2-10 technician garage door repair company that buys Google Business Profile, SEO, local services, referral, or website-form leads and cannot consistently answer or qualify every inbound lead within five minutes.

Why this wedge:

- Urgency is real: garage door providers advertise stuck doors, broken springs, off-track doors, and doors that will not close as same-day or emergency jobs.
- Lead value is high enough to justify software: 2025 public cost guides put common spring replacement around $150-$350, with broader repairs often reaching $150-$600.
- The workflow is narrow: common questions cluster around location, door issue, timing, price range, safety, and booking. That matches a constrained FAQ/RAG plus human approval product.
- The market has visible local targets: many DFW operators publicly advertise 24/7, same-day, or emergency service.

## Buyer Persona

Persona: hands-on owner/operator who still handles dispatch or manages one dispatcher.

Current workaround:

- Calls forward to the owner, dispatcher, or technician phones after hours.
- Website forms and missed calls are manually checked between jobs.
- The first available person asks for address, door type, problem, urgency, photos, and availability, then books or promises a callback.
- Risky answers about exact pricing, warranty, or safety are handled manually.

Buying trigger:

- Paid lead cost is rising or Google Business Profile volume is meaningful, but after-hours and busy-hour leads are leaking.
- The owner can name recent jobs lost because the customer called another company first.
- The company wants faster replies without hiring another dispatcher or outsourcing all call handling.

## Rejected Alternatives

| Vertical | Reason rejected for first wedge |
|----------|---------------------------------|
| HVAC emergency repair | Strong urgency and lead value, but seasonality, financing, dispatch complexity, and entrenched call-center workflows make the first pilot heavier. |
| Plumbing emergency repair | Strong urgency, but scope, licensing, safety claims, and broad issue taxonomy increase unsafe-answer risk for the first pilot. |
| Roofing storm repair | Lead value is high, but sales cycles are longer, insurance questions are risky, and urgency is event-driven rather than continuous. |
| Med spa inquiries | Easier scheduling, but response pain is less urgent and medical/regulated claims raise approval burden. |
| Legal intake | High lead value, but compliance and unauthorized-advice risk are too high for the current T1 runtime. |

## Baseline Metrics To Validate

These are measurement hypotheses for the first two-week pilot, not proven customer facts. Replace them with call logs, form timestamps, Google Business Profile data, and CRM/job records before claiming ROI.

| Metric | Starting hypothesis | How to measure | Pass/fail threshold for pilot |
|--------|---------------------|----------------|-------------------------------|
| Median first response time | Business hours: under 10 minutes; after hours or truck-busy windows: 20-60 minutes | Timestamp inbound lead to first human or agent response | Agent median under 2 minutes; human-review cases under 15 minutes |
| Missed lead rate | 20-35% of phone/form leads receive no live response or same-hour reply during busy/after-hours windows | Missed calls plus stale forms divided by total inbound leads | Reduce missed/stale leads by 30% without unsafe sends |
| Booking rate | 35-55% of contacted inbound repair leads book a visit | Booked jobs divided by qualified inbound leads | Improve booking rate by 10% relative or recover at least 3 extra booked jobs in two weeks |
| Manual review cost | 3-5 minutes per reviewed lead; roughly $0.90-$1.50 at $18/hour dispatcher cost | Operator review minutes multiplied by loaded hourly cost | Median review time under 90 seconds for edge cases |

## Value Hypothesis

If the agent responds to new leads within two minutes, collects the basic qualification fields, answers only from approved policy text, and routes risky cases to a human, then an owner/operator can recover missed after-hours or busy-hour jobs without hiring another dispatcher.

Minimum ROI bar for a pilot:

- Recover at least 3 additional booked jobs in two weeks, or
- Reduce median first response time below 2 minutes while maintaining zero unsafe autonomous replies, and
- Keep operator review time low enough that the owner trusts the workflow.

## Public Evidence

- Invoca reports that missed sales calls cost home services companies marketing spend and notes that fewer than 3% of callers pushed to voicemail leave a message: https://www.invoca.com/blog/how-much-missed-sales-calls-cost-home-services-businesses
- Invoca's missed-call product launch cited 26% of sales calls unanswered across industries and only 2% voicemail follow-through in aggregate customer data: https://www.invoca.com/press-release/invoca-launches-new-solution-to-recover-revenue-from-missed-sales-and-appointment-setting-calls
- Forbes Business Council summarizes speed-to-lead research, including materially higher connection odds within five minutes and historical slow-response benchmarks: https://www.forbes.com/councils/forbesbusinesscouncil/2025/09/04/why-your-response-time-is-still-costing-you-business-in-2025-and-how-to-fix-it/
- Angi's 2025 garage door spring guide lists $250 average spring replacement cost and a $150-$350 normal range: https://www.angi.com/articles/how-much-should-garage-door-spring-replacement-cost.htm/
- A1 Garage's 2025 garage door repair guide lists common garage door repairs around $150-$600 and highlights stuck cars or exposed homes as urgent cases: https://a1garage.com/https/a1garagecom/garage-door-repair-costs-in-2025/
- Local DFW providers publicly advertising same-day, emergency, or 24/7 repair include Express Garage Door Services, Viking Overhead, Longhorn Garage Doors & Gates, Paschal Gates & Garage Doors, Superior Overhead Door, Precision Door Fort Worth, and OGD Fort Worth.

## Validation Plan

Talk to 10 target accounts and require at least 5 confirmations of real urgent pain before building vertical-specific automation beyond the current console/API.

Confirmation means the buyer can show or describe at least one of:

- missed calls or stale form leads from the last 30 days
- paid leads that were not reached within one hour
- after-hours calls that went to voicemail
- owner/dispatcher overload during technician routes
- lost jobs where speed was the stated reason

Disqualify the vertical if fewer than 5 of the first 10 targets confirm the pain, or if target buyers already have a reliable answering service with tracked booking ROI.
