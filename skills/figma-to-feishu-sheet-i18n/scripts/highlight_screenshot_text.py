#!/usr/bin/env python3
"""Draw text-node highlight boxes onto Figma screenshots using Figma bounds."""

from __future__ import annotations

import json
import struct
import sys
import zlib
from pathlib import Path
from typing import Any


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SUPPORTED_COLOR_TYPES = {2, 6}
DEFAULT_COLOR = (255, 77, 79, 255)
DEFAULT_PADDING = 6
DEFAULT_STROKE_WIDTH = 4


class PngError(ValueError):
    """Raised when a PNG cannot be processed safely."""


def parse_bounds(value: object, field_name: str) -> dict[str, float]:
    """Parse a Figma bounds object with x, y, width, and height."""
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object")
    bounds: dict[str, float] = {}
    for key in ("x", "y", "width", "height"):
        raw_value = value.get(key)
        if raw_value is None:
            raise ValueError(f"{field_name}.{key} is required")
        bounds[key] = float(raw_value)
    if bounds["width"] <= 0 or bounds["height"] <= 0:
        raise ValueError(f"{field_name} width and height must be positive")
    return bounds


def read_png(path: Path) -> tuple[int, int, list[list[tuple[int, int, int, int]]]]:
    """Read an 8-bit RGB/RGBA non-interlaced PNG into RGBA pixels."""
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise PngError(f"Not a PNG: {path}")

    offset = len(PNG_SIGNATURE)
    width = height = color_type = bit_depth = interlace = None
    compressed = bytearray()

    while offset + 8 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        chunk_data = data[offset + 8 : offset + 8 + length]
        offset += 12 + length
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack(">IIBBBBB", chunk_data)
        elif chunk_type == b"IDAT":
            compressed.extend(chunk_data)
        elif chunk_type == b"IEND":
            break

    if width is None or height is None or color_type is None or bit_depth is None or interlace is None:
        raise PngError(f"Missing IHDR: {path}")
    if bit_depth != 8 or color_type not in SUPPORTED_COLOR_TYPES or interlace != 0:
        raise PngError(f"Unsupported PNG format: bit_depth={bit_depth}, color_type={color_type}, interlace={interlace}")

    channels = 4 if color_type == 6 else 3
    row_length = width * channels
    raw = zlib.decompress(bytes(compressed))
    expected_length = (row_length + 1) * height
    if len(raw) != expected_length:
        raise PngError(f"Unexpected PNG data length for {path}")

    rows: list[bytes] = []
    previous = bytearray(row_length)
    index = 0
    for _ in range(height):
        filter_type = raw[index]
        index += 1
        scanline = bytearray(raw[index : index + row_length])
        index += row_length
        unfiltered = unfilter_scanline(scanline, previous, filter_type, channels)
        rows.append(bytes(unfiltered))
        previous = unfiltered

    pixels: list[list[tuple[int, int, int, int]]] = []
    for row in rows:
        pixel_row: list[tuple[int, int, int, int]] = []
        for column in range(width):
            start = column * channels
            if channels == 4:
                pixel_row.append((row[start], row[start + 1], row[start + 2], row[start + 3]))
            else:
                pixel_row.append((row[start], row[start + 1], row[start + 2], 255))
        pixels.append(pixel_row)
    return width, height, pixels


def unfilter_scanline(scanline: bytearray, previous: bytearray, filter_type: int, bpp: int) -> bytearray:
    """Undo a PNG scanline filter."""
    result = bytearray(len(scanline))
    for index, value in enumerate(scanline):
        left = result[index - bpp] if index >= bpp else 0
        up = previous[index]
        upper_left = previous[index - bpp] if index >= bpp else 0
        if filter_type == 0:
            predictor = 0
        elif filter_type == 1:
            predictor = left
        elif filter_type == 2:
            predictor = up
        elif filter_type == 3:
            predictor = (left + up) // 2
        elif filter_type == 4:
            predictor = paeth_predictor(left, up, upper_left)
        else:
            raise PngError(f"Unsupported PNG filter type: {filter_type}")
        result[index] = (value + predictor) & 0xFF
    return result


def paeth_predictor(left: int, up: int, upper_left: int) -> int:
    """Return PNG Paeth predictor."""
    estimate = left + up - upper_left
    distance_left = abs(estimate - left)
    distance_up = abs(estimate - up)
    distance_upper_left = abs(estimate - upper_left)
    if distance_left <= distance_up and distance_left <= distance_upper_left:
        return left
    if distance_up <= distance_upper_left:
        return up
    return upper_left


def write_png(path: Path, width: int, height: int, pixels: list[list[tuple[int, int, int, int]]]) -> None:
    """Write RGBA pixels as a simple 8-bit non-interlaced PNG."""
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for red, green, blue, alpha in row:
            raw.extend((red, green, blue, alpha))

    def chunk(chunk_type: bytes, chunk_data: bytes) -> bytes:
        checksum = zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF
        return struct.pack(">I", len(chunk_data)) + chunk_type + chunk_data + struct.pack(">I", checksum)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    path.write_bytes(PNG_SIGNATURE + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def calculate_rect(
    image_width: int,
    image_height: int,
    screenshot_bounds: dict[str, float],
    text_bounds: dict[str, float],
    padding: int,
) -> tuple[int, int, int, int]:
    """Map Figma absolute text bounds into screenshot pixel coordinates."""
    scale_x = image_width / screenshot_bounds["width"]
    scale_y = image_height / screenshot_bounds["height"]
    left = round((text_bounds["x"] - screenshot_bounds["x"]) * scale_x) - padding
    top = round((text_bounds["y"] - screenshot_bounds["y"]) * scale_y) - padding
    right = round((text_bounds["x"] + text_bounds["width"] - screenshot_bounds["x"]) * scale_x) + padding
    bottom = round((text_bounds["y"] + text_bounds["height"] - screenshot_bounds["y"]) * scale_y) + padding
    left = max(0, min(image_width - 1, left))
    top = max(0, min(image_height - 1, top))
    right = max(left + 1, min(image_width - 1, right))
    bottom = max(top + 1, min(image_height - 1, bottom))
    return left, top, right, bottom


def draw_rect(
    pixels: list[list[tuple[int, int, int, int]]],
    rect: tuple[int, int, int, int],
    color: tuple[int, int, int, int],
    stroke_width: int,
) -> None:
    """Draw a rectangular border in-place."""
    left, top, right, bottom = rect
    for inset in range(stroke_width):
        current_left = left + inset
        current_top = top + inset
        current_right = right - inset
        current_bottom = bottom - inset
        if current_left > current_right or current_top > current_bottom:
            break
        for x in range(current_left, current_right + 1):
            pixels[current_top][x] = color
            pixels[current_bottom][x] = color
        for y in range(current_top, current_bottom + 1):
            pixels[y][current_left] = color
            pixels[y][current_right] = color


def highlighted_path_for(path: Path, suffix: str) -> Path:
    """Return default highlighted output path for a screenshot."""
    return path.with_name(f"{path.stem}{suffix}{path.suffix}")


def process_row(row: dict[str, Any], padding: int, stroke_width: int, suffix: str) -> dict[str, Any]:
    """Create highlighted screenshot for one row and return updated row metadata."""
    screenshot_path = Path(str(row.get("screenshot_path", "")).strip())
    if not screenshot_path:
        raise ValueError("screenshot_path is required")
    text_bounds = parse_bounds(row.get("text_bounds"), "text_bounds")
    screenshot_bounds = parse_bounds(row.get("screenshot_bounds"), "screenshot_bounds")
    width, height, pixels = read_png(screenshot_path)
    rect = calculate_rect(width, height, screenshot_bounds, text_bounds, padding)
    draw_rect(pixels, rect, DEFAULT_COLOR, stroke_width)
    output_path = Path(str(row.get("highlight_path", "")).strip()) if row.get("highlight_path") else highlighted_path_for(screenshot_path, suffix)
    write_png(output_path, width, height, pixels)
    next_row = dict(row)
    next_row["original_screenshot_path"] = str(screenshot_path)
    next_row["screenshot_path"] = str(output_path)
    next_row["highlight_path"] = str(output_path)
    next_row["highlight_rect"] = {"left": rect[0], "top": rect[1], "right": rect[2], "bottom": rect[3]}
    next_row["highlight_status"] = "ok"
    return next_row


def process_rows(rows: list[dict[str, Any]], padding: int, stroke_width: int, suffix: str) -> list[dict[str, Any]]:
    """Create highlighted screenshots for rows that have required metadata."""
    output: list[dict[str, Any]] = []
    for row in rows:
        try:
            output.append(process_row(row, padding, stroke_width, suffix))
        except (OSError, ValueError, PngError) as error:
            next_row = dict(row)
            next_row["highlight_status"] = f"skipped: {error}"
            output.append(next_row)
    return output


def main() -> int:
    """CLI entrypoint."""
    if len(sys.argv) not in {3, 5, 6}:
        print(
            "Usage: highlight_screenshot_text.py <rows.json> <output.json> "
            "[padding stroke_width [suffix]]"
        )
        return 1

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    padding = int(sys.argv[3]) if len(sys.argv) >= 5 else DEFAULT_PADDING
    stroke_width = int(sys.argv[4]) if len(sys.argv) >= 5 else DEFAULT_STROKE_WIDTH
    suffix = sys.argv[5] if len(sys.argv) == 6 else ".highlight"

    try:
        rows = json.loads(input_path.read_text())
        if not isinstance(rows, list):
            raise ValueError("input JSON must be a list of rows")
        output = process_rows(rows, padding, stroke_width, suffix)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}")
        return 1

    output_path.write_text(json.dumps(output, ensure_ascii=True, indent=2) + "\n")
    ok_count = sum(1 for row in output if row.get("highlight_status") == "ok")
    print(f"Wrote {len(output)} rows to {output_path}; highlighted {ok_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
