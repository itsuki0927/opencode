#!/usr/bin/env python3
"""Build final Feishu sheet rows from extracted Figma copy metadata."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


OPTIONAL_BOUND_KEYS = ("text_bounds", "screenshot_bounds")


def normalize_part(value: str, fallback: str) -> str:
    """Normalize semantic names into snake_case."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or fallback


def infer_role(source_text: str, node_name: str) -> str:
    """Infer a text role from copy and node metadata."""
    lower_text = source_text.strip().lower()
    lower_name = node_name.strip().lower()

    if "placeholder" in lower_name or lower_text.startswith(("enter ", "select ", "search ", "choose ")):
        return "placeholder"
    if any(token in lower_name for token in ["button", "btn"]) or lower_text in {
        "save",
        "submit",
        "confirm",
        "cancel",
        "continue",
        "publish",
        "create",
        "done",
    }:
        return "button"
    if any(token in lower_name for token in ["label"]):
        return "label"
    if any(token in lower_name for token in ["helper", "hint"]):
        return "helper"
    if any(token in lower_name for token in ["description", "desc"]):
        return "description"
    if any(token in lower_text for token in ["no data", "no results", "empty", "nothing found"]):
        return "empty_state"
    if len(lower_text.split()) <= 4:
        return "title"
    return "text"


def build_rows(items: list[dict[str, object]]) -> list[dict[str, object]]:
    """Convert extracted items into final row objects."""
    built_rows: list[dict[str, object]] = []
    used_keys: dict[str, str] = {}
    collisions: dict[str, int] = {}

    for item in items:
        source_text = str(item.get("source_text", "")).strip()
        if not source_text:
            continue

        page = normalize_part(str(item.get("page", "")), "page")
        module = normalize_part(str(item.get("module", "")), "module")
        role = normalize_part(str(item.get("role", "")), "") or infer_role(
            source_text,
            str(item.get("node_name", "")),
        )
        key = f"{page}_{module}_{role}"
        if key in used_keys and used_keys[key] != source_text:
            collisions[key] = collisions.get(key, 1) + 1
            key = f"{key}_{collisions[key]}"
        else:
            used_keys[key] = source_text

        row: dict[str, object] = {
            "key": key,
            "source_text": source_text,
            "context": f"page={page}; module={module}; role={role}; text={source_text}",
            "screenshot_node_id": str(item.get("screenshot_node_id", "")),
            "screenshot_path": str(item.get("screenshot_path", "")),
        }
        for bounds_key in OPTIONAL_BOUND_KEYS:
            if bounds_key in item:
                row[bounds_key] = item[bounds_key]
        built_rows.append(row)

    return built_rows


def main() -> int:
    """CLI entrypoint."""
    if len(sys.argv) != 3:
        print("Usage: build_sheet_rows.py <input.json> <output.json>")
        return 1

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    items = json.loads(input_path.read_text())
    rows = build_rows(items)
    output_path.write_text(json.dumps(rows, ensure_ascii=True, indent=2) + "\n")
    print(f"Wrote {len(rows)} rows to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
