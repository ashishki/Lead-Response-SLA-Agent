# Vertical Pack: Emergency Garage Door Repair

Date: 2026-05-20
Slug: `garage_door_repair`
Market: Dallas-Fort Worth same-day and 24/7 garage door repair

## Required Lead Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `customer_name` | yes | Human operator follow-up and dispatch record |
| `phone` | yes | Callback and SMS confirmation |
| `service_address_or_zip` | yes | Service-area check and route estimate |
| `door_issue` | yes | Qualification and technician prep |
| `urgency` | yes | Same-day, emergency, or scheduled triage |
| `door_type` | no | Residential, commercial, single, double, insulated, or unknown |
| `vehicle_trapped` | no | Prioritize blocked vehicle cases |
| `door_secure` | no | Escalate doors stuck open or security risks |
| `preferred_window` | no | Booking proposal |
| `photos_available` | no | Optional follow-up request |

## Qualification Questions

Ask only what is needed to book or route the job:

1. What city or ZIP code is the door in?
2. What is happening with the door: broken spring, opener issue, off track, cable, panel, stuck open, stuck closed, or something else?
3. Is the door stuck open, stuck closed, or is a vehicle trapped?
4. Is this residential or commercial?
5. Do you need same-day emergency help, or would a scheduled window work?
6. What phone number should the technician or dispatcher use?

## Approved FAQ Schema

Each approved source document must include:

- `source_document_id`
- `title`
- `category`: one of `service_area`, `pricing`, `booking`, `safety`, `service_scope`, `warranty`, `escalation`
- `approved_on`
- `owner`
- `text`

## Unsafe And Handoff Policy

| Category | Policy | Handoff reason |
|----------|--------|----------------|
| Exact pricing commitments | Give only approved ranges or say a technician/dispatcher must confirm after diagnosis. Never guarantee final price. | `pricing_commitment` |
| Arrival-time commitments | Offer approved windows only. Do not promise arrival before provider confirms capacity. | `booking_uncertainty` |
| Safety and DIY repair | Warn against DIY spring/cable repair and hand off if the customer asks for repair instructions. | `regulated_or_safety_advice` |
| Complaints or refund requests | Acknowledge and route to a human. Do not admit fault, negotiate refunds, or make warranty decisions. | `complaint_or_refund` |
| High-value commercial leads | Capture details and route to operator when commercial dock doors, roll-up doors, gates, or multi-door jobs appear. | `high_value_lead` |
| Unsupported policy | If the answer is not in approved text, create a human-review task with evidence IDs if available. | `unsupported_question` |
| Uncertain booking acceptance | If the customer has not explicitly accepted a proposed window, do not book. | `booking_without_acceptance` |

## Operator Scripts

Review queue opening:

> Confirm service area, issue type, urgency, and any safety/security risk. Approve only if the draft stays within approved pricing and booking language.

Pricing edit:

> Replace exact-price language with the approved range and note that final pricing depends on diagnosis.

No-send reason:

> Mark no-send if the draft promises exact arrival, exact final price, DIY spring/cable instructions, warranty approval, or refund terms.

High-value handoff:

> For commercial, gate, dock, or multi-door jobs, collect company/site details and route to the owner or commercial dispatcher before quoting.

## Seed Files

- `seed/verticals/garage_door_repair/pack.json`
- `seed/verticals/garage_door_repair/corpus.json`
- `seed/verticals/garage_door_repair/retrieval_eval.json`
- `seed/verticals/garage_door_repair/demo_tenant.json`
