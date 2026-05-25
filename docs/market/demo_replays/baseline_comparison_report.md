# Garage Door Baseline Comparison

Status: generated
Generated on: 2026-05-25
Data classification: synthetic controlled baseline

| mode | correct_next_action_rate | unsafe_claim_count | human_approval_violation_count | notes |
|---|---:|---:|---:|---|
| manual_template_baseline | 0.24 | 4 | 38 | Fast but brittle; cannot reason over public evidence, tenant policy, or provider failures. |
| llm_no_rag_baseline | 0.72 | 4 | 14 | Better language quality, but lacks source grounding and deterministic tool/failure gates. |
| agent_rag_tool_use | 1.0 | 0 | 0 | Uses public corpus, policy gates, tool/failure metadata, and human approval for every send. |

## Claim Boundary

Baseline comparison is controlled pre-pilot evidence. It does not prove production ROI, conversion lift, autonomous-send safety, or live-client results.
