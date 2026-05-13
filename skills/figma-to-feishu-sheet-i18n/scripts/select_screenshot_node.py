#!/usr/bin/env python3
"""Select nearest usable screenshot container from ancestor metadata."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


CONTAINER_TYPES = {"FRAME", "GROUP", "COMPONENT", "INSTANCE", "SECTION"}
NAME_HINTS = (
    "button",
    "input",
    "field",
    "card",
    "modal",
    "dialog",
    "section",
    "panel",
    "empty",
    "form",
    "header",
    "footer",
)


def area(node: dict[str, object]) -> float:
    """Return node area from width and height."""
    width = float(node.get("width", 0) or 0)
    height = float(node.get("height", 0) or 0)
    return width * height


def candidate_score(node: dict[str, object], page_area: float) -> float:
    """Score candidate node. Higher is better."""
    node_type = str(node.get("type", "")).upper()
    width = float(node.get("width", 0) or 0)
    height = float(node.get("height", 0) or 0)
    node_area = area(node)
    name = str(node.get("name", "")).lower()

    if node_type not in CONTAINER_TYPES:
        return -math.inf
    if width < 120 or height < 40:
        return -math.inf
    if page_area > 0 and node_area / page_area > 0.85:
        return -50.0

    score = 0.0
    score += 30.0 if node_type in {"COMPONENT", "INSTANCE"} else 20.0
    score -= max(0.0, (node_area / page_area) * 20.0) if page_area else 0.0
    score += 8.0 if any(hint in name for hint in NAME_HINTS) else 0.0
    score -= 0.1 * max(0.0, width - 800.0)
    return score


def select_candidate(row: dict[str, object]) -> dict[str, object] | None:
    """Pick best screenshot candidate for a single text row."""
    ancestors = list(row.get("ancestors", []))
    page = row.get("page", {})
    page_area = area(page) if isinstance(page, dict) else 0.0

    best: dict[str, object] | None = None
    best_score = -math.inf
    for candidate in ancestors:
        if not isinstance(candidate, dict):
            continue
        score = candidate_score(candidate, page_area)
        if score > best_score:
            best = candidate
            best_score = score

    if best is not None:
        return best
    if isinstance(page, dict) and page.get("id"):
        return page
    return None


def main() -> int:
    """CLI entrypoint."""
    if len(sys.argv) != 3:
        print("Usage: select_screenshot_node.py <input.json> <output.json>")
        return 1

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    rows = json.loads(input_path.read_text())
    output: list[dict[str, object]] = []

    for row in rows:
        chosen = select_candidate(row)
        next_row = dict(row)
        if chosen is not None:
            next_row["screenshot_node_id"] = chosen.get("id", "")
            next_row["screenshot_node_name"] = chosen.get("name", "")
        output.append(next_row)

    output_path.write_text(json.dumps(output, ensure_ascii=True, indent=2) + "\n")
    print(f"Wrote {len(output)} rows to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
