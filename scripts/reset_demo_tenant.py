#!/usr/bin/env python
"""Reset the sales demo tenant to a known PII-free state."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_TEMPLATE = Path("seed/demo_tenant/template.json")
DEFAULT_OUTPUT = Path("seed/demo_tenant/state.json")


def build_demo_state(template_path: Path = DEFAULT_TEMPLATE) -> dict[str, Any]:
    payload = json.loads(template_path.read_text(encoding="utf-8"))
    required_scenarios = {
        "supported_faq",
        "unsupported_handoff",
        "booking_proposal",
    }
    scenarios = {lead["scenario"] for lead in payload["leads"]}
    if not required_scenarios <= scenarios:
        raise ValueError("demo tenant template is missing required sales scenarios")
    if not any(task["scenario"] == "operator_approval" for task in payload["review_tasks"]):
        raise ValueError("demo tenant template is missing operator approval scenario")
    return payload


def reset_demo_tenant(
    output_path: Path = DEFAULT_OUTPUT,
    template_path: Path = DEFAULT_TEMPLATE,
) -> dict[str, Any]:
    state = build_demo_state(template_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset the sales demo tenant state.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    args = parser.parse_args()

    state = reset_demo_tenant(output_path=args.output, template_path=args.template)
    print(
        json.dumps(
            {
                "schema_version": state["schema_version"],
                "tenant_id": state["tenant"]["tenant_id"],
                "lead_count": len(state["leads"]),
                "review_task_count": len(state["review_tasks"]),
                "reset_path": str(args.output),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
