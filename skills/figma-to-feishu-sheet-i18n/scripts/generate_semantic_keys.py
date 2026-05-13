#!/usr/bin/env python3
"""Generate semantic page_module_item keys from row JSON."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROLE_KEYWORDS: list[tuple[str, list[str]]] = [
    ("empty_state_title", ["no ", "nothing ", "empty ", "no data", "no results"]),
    ("placeholder", ["enter ", "select ", "search ", "choose "]),
    ("button", ["save", "submit", "confirm", "cancel", "continue", "done", "publish", "create", "next"]),
    ("title", []),
]


def normalize_part(value: str, fallback: str) -> str:
    """Normalize a single key segment into snake_case."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or fallback


def infer_item(row: dict[str, str]) -> str:
    """Infer item role for the key suffix."""
    role = normalize_part(row.get("role", ""), "")
    if role:
        return role

    source_text = row.get("source_text", "").strip().lower()
    node_name = row.get("node_name", "").strip().lower()

    if "placeholder" in node_name:
        return "placeholder"
    if any(keyword in node_name for keyword in ["button", "btn"]):
        return "button"
    if any(keyword in node_name for keyword in ["title", "heading", "header"]):
        return "title"
    if any(keyword in node_name for keyword in ["subtitle", "sub_title"]):
        return "subtitle"
    if any(keyword in node_name for keyword in ["label"]):
        return "label"
    if any(keyword in node_name for keyword in ["helper", "hint"]):
        return "helper"
    if any(keyword in node_name for keyword in ["description", "desc"]):
        return "description"

    for item, keywords in ROLE_KEYWORDS:
        if keywords and any(source_text.startswith(keyword) for keyword in keywords):
            return item

    if len(source_text.split()) <= 4:
        return "title"
    return "text"


def generate_keys(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return rows with deterministic semantic keys."""
    seen: dict[str, str] = {}
    collisions: dict[str, int] = {}
    output: list[dict[str, str]] = []

    for row in rows:
        page = normalize_part(row.get("page", ""), "page")
        module = normalize_part(row.get("module", ""), "module")
        item = infer_item(row)
        key = f"{page}_{module}_{item}"
        source_text = row.get("source_text", "")

        if key in seen and seen[key] != source_text:
            collisions[key] = collisions.get(key, 1) + 1
            key = f"{key}_{collisions[key]}"
        else:
            seen[key] = source_text

        next_row = dict(row)
        next_row["key"] = key
        output.append(next_row)

    return output


def main() -> int:
    """CLI entrypoint."""
    if len(sys.argv) != 3:
        print("Usage: generate_semantic_keys.py <input.json> <output.json>")
        return 1

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    rows = json.loads(input_path.read_text())
    output_path.write_text(json.dumps(generate_keys(rows), ensure_ascii=True, indent=2) + "\n")
    print(f"Wrote {len(rows)} rows to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
