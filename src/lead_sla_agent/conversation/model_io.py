"""Deterministic model-IO placeholders for the bounded loop."""

from __future__ import annotations


def qualifying_question_for(field_name: str) -> str:
    questions = {
        "contact_name": "What name should we use for this request?",
        "contact_phone": "What phone number should we use for follow-up?",
    }
    return questions.get(field_name, f"Can you share {field_name}?")
