# Pilot Measurement Plan

Date: 2026-05-20
Vertical: DFW emergency garage door repair
Status: buyer-review draft

## Measurement Goal

Prove whether Lead Response SLA Agent creates economic value by improving response speed, lead capture, booked calls, and qualified handoffs without increasing unsafe automation or operator workload.

The buyer should agree before launch that these metrics are sufficient to justify payment, expansion, or cancellation.

## Measurement Periods

| Period | Dates | Purpose |
|--------|-------|---------|
| Baseline period | 14 calendar days before pilot start | Measure current response time, missed lead rate, booking rate, qualified handoffs, review/dispatch effort, and cost per lead. |
| Pilot period | First 14 calendar days with the agent enabled | Compare the same metrics while the agent handles acknowledgement, qualification, safe FAQ replies, and human-review routing. |
| Weekly buyer update | Every 7 days during pilot | Review outcomes, incidents, operator corrections, and whether value is tracking toward payment. |

Do not compare a busy storm week against a quiet baseline without noting the demand change. If lead volume differs by more than 25 percent, report normalized rates alongside raw counts.

## Source Data

| Data source | Fields needed | Owner |
|-------------|---------------|-------|
| Phone/call tracking | inbound timestamp, answered/missed status, callback timestamp, booked job flag | buyer |
| Website forms | submitted timestamp, first response timestamp, source channel, booked job flag | buyer |
| Agent analytics | first-response p50/p95, automation success, human-review rate, provider send failures | system |
| Operator review | review count, no-send count, approved edits, average review time | operator |
| Outcome labels | booked, qualified handoff, lost, no response, disqualified | operator |
| Spend or lead source data | paid lead count, rough spend, source channel | buyer |

## Metrics

| Metric | Definition | Baseline | Pilot target |
|--------|------------|----------|--------------|
| Response time p50/p95 | Time from inbound lead to first human or agent response | Baseline call/form logs | p50 under 2 minutes; p95 under 30 seconds for AI-eligible first replies |
| Lead capture rate | Leads with enough contact and issue data to follow up | Captured leads divided by inbound leads | 20 percent relative lift or clear recovery of stale leads |
| Booked calls/jobs | Leads marked `booked` | Booked labels divided by qualified inbound leads | 10 percent relative lift or at least 3 incremental booked jobs in 14 days |
| Qualified handoffs | Leads routed to human with clear issue, urgency, contact, and evidence/context | Baseline manual handoff count and quality notes | More complete handoffs without extra dispatcher effort |
| Human-review rate | Human-review tasks divided by inbound leads | n/a if no current queue; use dispatcher review time | Under 30 percent after first week unless safety requires more |
| Cost per lead handled | Software plus operator review cost divided by handled inbound leads | Dispatcher/owner time cost and answering-service cost | Lower than hiring/outsourcing equivalent, or offset by recovered bookings |
| Provider send failures | Failed outbound sends divided by attempted sends | n/a or current provider failure logs | Under 2 percent; any sustained outage reported |
| Unsafe automation | Customer-facing autonomous replies that violate policy | Baseline zero-tolerance | Zero |

## Success Criteria

Strong pilot:

- At least 3 incremental booked jobs or a 10 percent relative booked-rate lift.
- Median first response under 2 minutes for eligible leads.
- Zero unsafe autonomous replies.
- Buyer says the weekly report explains value clearly enough to justify payment.

Weak pilot:

- Faster response but no lift in booked calls, qualified handoffs, or recovered leads.
- Human-review rate stays above 50 percent because knowledge/policy coverage is too thin.
- Buyer cannot connect the report to revenue or labor savings.

Pivot or stop:

- Buyer cannot provide baseline data.
- Lead volume is too low to measure within 14 days.
- Existing answering service already responds quickly and books reliably.
- Safety constraints force nearly every lead to manual review.

## Before Launch Checklist

- Buyer approves baseline and pilot dates.
- Buyer agrees which outcome labels count as booked, qualified handoff, lost, no response, and disqualified.
- Buyer names the person responsible for weekly outcome labels.
- Operator confirms no raw customer PII will be pasted into report notes.
- Buyer agrees that payment/expansion decision will use this metric set.
