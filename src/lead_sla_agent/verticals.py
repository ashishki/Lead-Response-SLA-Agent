"""Vertical pack loading helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VerticalPack:
    slug: str
    config: dict[str, Any]
    demo_tenant: dict[str, Any]
    corpus_documents: list[dict[str, Any]]
    eval_cases: list[dict[str, Any]]


def load_vertical_pack(slug: str, base_path: Path = Path("seed/verticals")) -> VerticalPack:
    pack_path = base_path / slug
    if not pack_path.exists():
        raise FileNotFoundError(f"vertical pack not found: {slug}")

    config = _read_json(pack_path / "pack.json")
    if config.get("slug") != slug:
        raise ValueError("vertical pack slug mismatch")

    corpus = _read_json(pack_path / "corpus.json")
    eval_dataset = _read_json(pack_path / "retrieval_eval.json")
    demo_tenant = _read_json(pack_path / "demo_tenant.json")

    return VerticalPack(
        slug=slug,
        config=config,
        demo_tenant=demo_tenant,
        corpus_documents=list(corpus["documents"]),
        eval_cases=list(eval_dataset["queries"]),
    )


def initialize_demo_tenant(slug: str, base_path: Path = Path("seed/verticals")) -> dict[str, Any]:
    pack = load_vertical_pack(slug, base_path)
    return {
        "tenant": pack.demo_tenant["tenant"],
        "knowledge_documents": pack.corpus_documents,
        "retrieval_eval_queries": pack.eval_cases,
        "required_lead_fields": pack.config["required_lead_fields"],
        "handoff_reasons": pack.config["handoff_reasons"],
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
