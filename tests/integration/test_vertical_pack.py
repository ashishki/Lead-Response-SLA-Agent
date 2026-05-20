from __future__ import annotations

from lead_sla_agent.verticals import initialize_demo_tenant, load_vertical_pack


def test_garage_door_vertical_pack_defines_policy_and_questions() -> None:
    pack = load_vertical_pack("garage_door_repair")

    assert pack.config["schema_version"] == "vertical-pack-v1"
    assert pack.config["required_lead_fields"] == [
        "customer_name",
        "phone",
        "service_address_or_zip",
        "door_issue",
        "urgency",
    ]
    assert len(pack.config["qualification_questions"]) >= 6
    for handoff_reason in (
        "pricing_commitment",
        "booking_uncertainty",
        "regulated_or_safety_advice",
        "complaint_or_refund",
        "high_value_lead",
        "booking_without_acceptance",
    ):
        assert handoff_reason in pack.config["handoff_reasons"]


def test_garage_door_vertical_pack_includes_corpus_and_eval_dataset() -> None:
    pack = load_vertical_pack("garage_door_repair")
    document_ids = {document["source_document_id"] for document in pack.corpus_documents}
    eval_slices = {case["slice"] for case in pack.eval_cases}

    assert document_ids >= {
        "gd-service-area",
        "gd-pricing-ranges",
        "gd-booking-policy",
        "gd-safety-policy",
        "gd-commercial-escalation",
    }
    assert eval_slices >= {
        "service_area",
        "pricing",
        "booking",
        "safety",
        "high_value",
        "unsupported",
    }
    for case in pack.eval_cases:
        assert set(case["expected_source_document_ids"]) <= document_ids


def test_garage_door_pack_initializes_demo_tenant() -> None:
    demo = initialize_demo_tenant("garage_door_repair")

    assert demo["tenant"]["slug"] == "dfw-garage-door-demo"
    assert demo["tenant"]["timezone"] == "America/Chicago"
    assert len(demo["knowledge_documents"]) == 5
    assert len(demo["retrieval_eval_queries"]) >= 6
    assert "phone" in demo["required_lead_fields"]
    assert "booking_without_acceptance" in demo["handoff_reasons"]
