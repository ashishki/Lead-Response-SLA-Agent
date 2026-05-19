from __future__ import annotations

import logging

from lead_sla_agent.observability.logging import PIIRedactingFilter


def test_pii_values_are_not_logged(caplog) -> None:
    logger = logging.getLogger("lead_sla_agent.tests.pii")
    logger.addFilter(PIIRedactingFilter())

    raw_values = {
        "name": "Test Person",
        "phone": "+15550101010",
        "email": "lead@example.test",
        "message": "Need help with my booking",
    }

    with caplog.at_level(logging.INFO, logger=logger.name):
        logger.info("lead_event %s", raw_values)

    logged_text = caplog.text
    for raw_value in raw_values.values():
        assert raw_value not in logged_text

    assert "[redacted]" in logged_text
    assert "sha256:" in logged_text
