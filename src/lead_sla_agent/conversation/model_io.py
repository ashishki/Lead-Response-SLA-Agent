"""Deterministic model-IO placeholders for the bounded loop."""

from __future__ import annotations

from dataclasses import dataclass

MODEL_OUTPUT_SCHEMA_VERSION = "model-output-schema-v1"
QUALIFICATION_PROMPT_VERSION = "qualification-prompt-v1"
ACKNOWLEDGEMENT_PROMPT_VERSION = "acknowledgement-prompt-v1"
DEFAULT_MODEL_NAME = "deterministic-runtime-v1"


@dataclass(frozen=True)
class ModelOutputRecord:
    model_name: str
    prompt_version: str
    schema_version: str
    policy_decision: str
    output_text: str | None


def qualifying_question_for(field_name: str) -> str:
    questions = {
        "contact_name": "What name should we use for this request?",
        "contact_phone": "What phone number should we use for follow-up?",
    }
    return questions.get(field_name, f"Can you share {field_name}?")


def model_output_record(
    output_text: str | None,
    prompt_version: str,
    policy_decision: str,
    model_name: str = DEFAULT_MODEL_NAME,
) -> ModelOutputRecord:
    """Build versioned metadata for every model-like output."""
    return ModelOutputRecord(
        model_name=model_name,
        prompt_version=prompt_version,
        schema_version=MODEL_OUTPUT_SCHEMA_VERSION,
        policy_decision=policy_decision,
        output_text=output_text,
    )
