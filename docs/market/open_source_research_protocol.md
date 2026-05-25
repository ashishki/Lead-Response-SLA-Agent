# Public Vertical Research Protocol

Status: active
Date: 2026-05-23

This protocol is mandatory for solo demo-pack work when there is no signed pilot
tenant, no private lead logs, and no customer-approved knowledge base. The agent
must gather public vertical evidence and create demo-safe artifacts instead of
waiting for business access.

This protocol supports public-source research only. It does not authorize
private data collection, automated outreach, autonomous customer sends,
paid production readiness claims, paid production launch claims,
conversion-lift claims, or ROI claims.

## When To Research

Use public research when a task needs:

- vertical selection evidence;
- service-area, FAQ, booking, escalation, or qualification examples;
- a knowledge-pack seed;
- realistic lead scenarios;
- public competitor/service examples;
- buyer-target lists for manual outreach.

## Allowed Sources

- Public business websites and landing pages.
- Public FAQs, service pages, pricing-range pages, booking/contact pages, and
  policy pages.
- Public Google Business Profile-style snippets only when captured as links or
  short notes, not scraped private data.
- Public industry guides and service-cost guides.
- Public directories when used only to create a manually reviewed target list.
- Public review themes only as aggregate operational signals, never as copied
  reviewer names, phone numbers, addresses, message text, or individual claims.

## Forbidden Sources

- Private lead logs, CRM exports, call recordings, inboxes, paid lead portals,
  or customer messages without explicit approval.
- Non-public customer messages, quote requests, support tickets, dispatch notes,
  booking records, or transcript text.
- Raw phone/email/person names in committed target lists unless already public
  and necessary for manual outreach.
- Scraped personal data, copied review text, private social profiles, or contact
  enrichment databases.
- Unsupported conversion, ROI, revenue, missed-revenue, or booking-lift claims
  from public demo data.
- Claims that the product is paid-production-ready or safe for autonomous send
  before real pilot evidence and human approval exist.
- Autonomous outbound contact.

## Required Source Register

Every vertical research artifact must include:

| Field | Required |
|---|---|
| source_url_or_locator | yes |
| captured_at | yes |
| company_or_source_type | yes |
| evidence_kind | yes |
| extracted_fact | yes |
| demo_use | yes |
| limitation | yes |
| pii_contact_handling | yes |

Examples of `evidence_kind`: `service_area`, `faq`, `pricing_range`,
`booking_rule`, `emergency_claim`, `handoff_boundary`, `competitor_note`.

## Claim Rule

Public vertical research may support a demo knowledge pack, synthetic lead
scenario bank, and outreach target list. It does not prove conversion lift,
customer willingness to pay, or autonomous-send safety. Those require real
pilot evidence.

Allowed public-demo claims:

- "This demo uses public-source evidence and synthetic lead scenarios."
- "The system can show how it would acknowledge, qualify, retrieve approved
  knowledge, and route risky cases to human review."
- "The next proof step is a real pilot using approved customer data and measured
  response, booking, safety, and operator workload outcomes."

Blocked public-demo claims:

- "This improves conversion by X percent."
- "This recovers $X in missed revenue."
- "This is ready for paid production."
- "This can autonomously send customer replies without human approval."
- "Public competitor data proves buyer willingness to pay."

## Demo Artifact Rules

- Label all generated leads and replay artifacts as synthetic demo data.
- Cite source URLs or source-register IDs for every fact used in a knowledge
  pack, scenario, demo report, or target-list rationale.
- Mark assumptions separately from cited facts.
- Route unsupported, stale, risky, exact-pricing, warranty, legal, safety, or
  high-commitment answers to human review.
- Use the protocol again when a later task lacks enough data instead of stopping
  for private customer access.
