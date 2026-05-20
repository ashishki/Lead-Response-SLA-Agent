# Customer Communication Templates

Use these templates for pilot customer updates. Keep all customer data out of the message.

## Provider Outage

Subject: Lead response provider issue detected

We detected an issue with `[provider/channel]` affecting `[workflow]` for your pilot.

Current impact:

- New leads: `[accepted/degraded/blocked]`
- Outbound responses: `[working/degraded/paused]`
- Human-review fallback: `[active/not needed]`
- Data exposure: `none known`

What we are doing:

- routing affected work to the safest available fallback
- monitoring queue depth and provider recovery
- retrying failed sends only after the provider is stable

Next update: `[time]`

## Provider Outage Resolved

Subject: Lead response provider issue resolved

The `[provider/channel]` issue is resolved.

Summary:

- Impact window: `[start]` to `[end]`
- Leads affected: `[count or unknown]`
- Failed sends: `[count or unknown]`
- Human-review fallback used: `[yes/no]`

We will include the incident in the next weekly report and note any prevention tasks.

## AI Safety Handoff

Subject: Lead routed to human review for safety

The agent routed a lead to human review instead of sending an autonomous reply.

Reason category: `[pricing_commitment / safety_advice / complaint / high_value_lead / unsupported_question / booking_uncertainty]`

What happened:

- The draft required operator review under the pilot policy.
- No unsafe autonomous reply was sent.
- An operator can approve, edit, or no-send the response.

Next step: `[operator action needed / already handled]`

## AI Safety Incident

Subject: Safety review opened for lead response

We opened a safety review for the pilot.

Current status:

- Autonomous sends for affected category: `[paused/not paused]`
- Human-review fallback: `[active]`
- Customer data exposure: `[none known / under review]`
- Next update: `[time]`

We will provide a post-incident review with root cause and prevention tasks.
