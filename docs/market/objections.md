# Objection Handling

Use this document in sales conversations and pilot reviews. Keep responses grounded in measurable lead recovery and operational safety.

## Safety

Objection: "I do not trust AI to talk to customers."

Response: "The agent is constrained. It answers only from approved text and routes exact pricing, safety advice, complaints, high-value commercial leads, unsupported questions, and uncertain bookings to human review. The weekly report includes unsafe autonomous replies as a zero-tolerance metric."

Proof to show:

- operator review queue
- no-send path
- approved corpus
- eval and incident evidence

## Data

Objection: "What happens to customer data?"

Response: "Tenant exports identify PII fields, retention is configurable, and delete requests use anonymization with an audit record. Reports do not include raw customer names, phone numbers, emails, message text, provider IDs, or transcripts."

Proof to show:

- data retention/export/delete runbook
- tenant export schema
- PII-free metrics contract

## Integration

Objection: "This sounds like a big integration project."

Response: "The first pilot uses one inbound source and one outbound channel. The vertical pack already defines required lead fields, garage door policies, operator scripts, and seed knowledge. CRM/calendar integration can stay fake or manual until response-time and booking lift are proven."

Proof to show:

- garage door vertical pack
- provider adapter tests
- weekly report template

## Pricing

Objection: "This is too expensive."

Response: "We are testing pricing against recovered booked jobs and review workload, not AI usage. We can use a small recovery pilot, pay-per-incremental-booked-job, or dispatcher-assist package depending on how you already buy call handling and leads."

Proof to show:

- pricing hypotheses
- pilot terms
- measurement plan

## Attribution

Objection: "How do I know the agent caused the booking lift?"

Response: "We define a baseline period and pilot period before launch, track source timestamps, and label outcomes weekly. If lead volume changes by more than 25 percent, we report normalized rates as well as raw counts."

Proof to show:

- pilot measurement plan
- weekly buyer report

## Current Vendor

Objection: "We already use an answering service."

Response: "Then the test is not generic response coverage. The test is whether the answering service misses after-hours/forms, whether it books reliably, and whether AI-assisted handoff reduces owner review. If your current service already proves that, this may not be the right wedge."

Proof to show:

- missed-lead baseline
- booking-rate baseline
- review-time comparison
