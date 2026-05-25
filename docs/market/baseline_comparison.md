# Baseline Comparison

Status: generated summary
Date: 2026-05-25

This is part of the pre-pilot evidence package.

Source artifact:
`docs/market/demo_replays/baseline_comparison_report.json`

## Modes

| Mode | Description |
|---|---|
| `manual_template_baseline` | Simple static reply templates without retrieval, policy reasoning, or tool/failure state. |
| `llm_no_rag_baseline` | Generic language model behavior without public corpus grounding or deterministic tool gates. |
| `agent_rag_tool_use` | Current controlled agent path with public corpus grounding, policy gates, tool/failure metadata, and human approval. |

## Result

| Mode | Correct next-action rate | Unsafe claim count | Human-approval violations |
|---|---:|---:|---:|
| `manual_template_baseline` | 0.24 | 4 | 38 |
| `llm_no_rag_baseline` | 0.72 | 4 | 14 |
| `agent_rag_tool_use` | 1.00 | 0 | 0 |

## Interpretation

This is a controlled comparison against public/synthetic scenarios. It supports
the claim that the current agent path is better prepared for a human-approved
pilot than simple templates or ungrounded model responses.

It does not prove production ROI, conversion lift, live-client proof,
autonomous-send safety, or paid production readiness.
