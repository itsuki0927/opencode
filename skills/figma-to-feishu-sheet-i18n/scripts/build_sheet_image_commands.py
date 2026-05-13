#!/usr/bin/env python3
"""Generate safe Feishu CLI commands for placing screenshot images in a sheet."""

from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path

from prepare_sheet_image import build_result


DEFAULT_MAX_WIDTH = 320
DEFAULT_MAX_HEIGHT = 180
FIRST_DATA_ROW = 3


def command_quote(value: str) -> str:
    """Return a shell-safe value."""
    return shlex.quote(value)


def build_commands(
    rows: list[dict[str, object]],
    spreadsheet_token: str,
    sheet_id: str,
    max_width: int = DEFAULT_MAX_WIDTH,
    max_height: int = DEFAULT_MAX_HEIGHT,
) -> list[str]:
    """Build upload and placement commands for rows with screenshot paths."""
    commands: list[str] = []
    missing_screenshot_rows: list[int] = []
    for index, row in enumerate(rows):
        screenshot_path = str(row.get("screenshot_path", "")).strip()
        if not screenshot_path:
            if str(row.get("screenshot_node_id", "")).strip():
                missing_screenshot_rows.append(FIRST_DATA_ROW + index)
            continue

        image_path = Path(screenshot_path)
        sizing = build_result(image_path, max_width, max_height)
        target_row = FIRST_DATA_ROW + index
        target_range = f"{sheet_id}!B{target_row}:B{target_row}"
        token_variable = f"IMAGE_TOKEN_{index}"

        commands.append(
            "UPLOAD_JSON=$(feishu-cli media upload "
            f"{command_quote(str(image_path))} --parent-type sheet_image "
            f"--parent-node {command_quote(spreadsheet_token)} -o json)"
        )
        commands.append(
            f"{token_variable}=$(python3 -c "
            + command_quote(
                "import json,sys; data=json.loads(sys.stdin.read()); "
                "print(data.get('file_token') or data.get('token') or data.get('image_token') or data.get('data', {}).get('file_token') or data.get('data', {}).get('token') or data.get('data', {}).get('image_token') or '')"
            )
            + " <<< \"$UPLOAD_JSON\")"
        )
        commands.append(f"test -n \"${token_variable}\"")
        commands.append(
            "feishu-cli sheet image add "
            f"{command_quote(spreadsheet_token)} {command_quote(sheet_id)} "
            f"--token \"${token_variable}\" "
            f"--range {command_quote(target_range)} "
            f"--width {sizing['width']} "
            f"--height {sizing['height']}"
        )

    commands.append(
        "feishu-cli sheet image list "
        f"{command_quote(spreadsheet_token)} {command_quote(sheet_id)} -o json"
    )
    if missing_screenshot_rows:
        rows_label = ", ".join(str(row_number) for row_number in missing_screenshot_rows)
        raise ValueError(
            "Rows have screenshot_node_id but empty screenshot_path; capture screenshots before image placement. "
            f"Affected sheet rows: {rows_label}"
        )
    if len(commands) == 1:
        raise ValueError("No screenshot_path values found; no sheet images can be uploaded or inserted")
    return commands


def main() -> int:
    """CLI entrypoint."""
    if len(sys.argv) not in {4, 6}:
        print(
            "Usage: build_sheet_image_commands.py <rows.json> <spreadsheet_token> <sheet_id> "
            "[max_width max_height]"
        )
        return 1

    rows_path = Path(sys.argv[1])
    spreadsheet_token = sys.argv[2]
    sheet_id = sys.argv[3]
    max_width = int(sys.argv[4]) if len(sys.argv) == 6 else DEFAULT_MAX_WIDTH
    max_height = int(sys.argv[5]) if len(sys.argv) == 6 else DEFAULT_MAX_HEIGHT

    try:
        rows = json.loads(rows_path.read_text())
        commands = build_commands(rows, spreadsheet_token, sheet_id, max_width, max_height)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}")
        return 1

    print("\n".join(commands))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
