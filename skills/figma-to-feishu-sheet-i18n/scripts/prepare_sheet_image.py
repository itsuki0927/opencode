#!/usr/bin/env python3
"""Calculate aspect-ratio-safe display dimensions for Feishu sheet images."""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path


MIN_DISPLAY_SIZE = 20
DEFAULT_MAX_WIDTH = 320
DEFAULT_MAX_HEIGHT = 180


def read_png_size(data: bytes) -> tuple[int, int] | None:
    """Return PNG dimensions from an IHDR chunk."""
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 24:
        return None
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def read_jpeg_size(data: bytes) -> tuple[int, int] | None:
    """Return JPEG dimensions from SOF markers."""
    if not data.startswith(b"\xff\xd8"):
        return None

    index = 2
    while index + 9 < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        index += 2
        if marker in {0xD8, 0xD9}:
            continue
        if index + 2 > len(data):
            return None
        segment_length = struct.unpack(">H", data[index : index + 2])[0]
        if segment_length < 2 or index + segment_length > len(data):
            return None
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            height, width = struct.unpack(">HH", data[index + 3 : index + 7])
            return width, height
        index += segment_length
    return None


def read_webp_size(data: bytes) -> tuple[int, int] | None:
    """Return WebP dimensions for VP8X, VP8L, and VP8 headers."""
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None

    chunk_type = data[12:16]
    if chunk_type == b"VP8X" and len(data) >= 30:
        width = int.from_bytes(data[24:27], "little") + 1
        height = int.from_bytes(data[27:30], "little") + 1
        return width, height
    if chunk_type == b"VP8L" and len(data) >= 25:
        bits = int.from_bytes(data[21:25], "little")
        width = (bits & 0x3FFF) + 1
        height = ((bits >> 14) & 0x3FFF) + 1
        return width, height
    if chunk_type == b"VP8 " and len(data) >= 30:
        width = struct.unpack("<H", data[26:28])[0] & 0x3FFF
        height = struct.unpack("<H", data[28:30])[0] & 0x3FFF
        return width, height
    return None


def read_image_size(path: Path) -> tuple[int, int]:
    """Read dimensions for PNG, JPEG, or WebP images without third-party dependencies."""
    data = path.read_bytes()
    size = read_png_size(data) or read_jpeg_size(data) or read_webp_size(data)
    if size is None:
        raise ValueError(f"Unsupported image format or unreadable dimensions: {path}")
    width, height = size
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid image dimensions for {path}: {width}x{height}")
    return width, height


def fit_dimensions(
    original_width: int,
    original_height: int,
    max_width: int = DEFAULT_MAX_WIDTH,
    max_height: int = DEFAULT_MAX_HEIGHT,
) -> tuple[int, int]:
    """Fit dimensions within a bounding box while preserving aspect ratio."""
    if max_width < MIN_DISPLAY_SIZE or max_height < MIN_DISPLAY_SIZE:
        raise ValueError(f"Max dimensions must be at least {MIN_DISPLAY_SIZE}px")

    scale = min(max_width / original_width, max_height / original_height, 1.0)
    display_width = max(MIN_DISPLAY_SIZE, round(original_width * scale))
    display_height = max(MIN_DISPLAY_SIZE, round(original_height * scale))
    return display_width, display_height


def build_result(path: Path, max_width: int, max_height: int) -> dict[str, int | str]:
    """Build JSON-serializable image sizing result."""
    original_width, original_height = read_image_size(path)
    display_width, display_height = fit_dimensions(original_width, original_height, max_width, max_height)
    return {
        "path": str(path),
        "original_width": original_width,
        "original_height": original_height,
        "width": display_width,
        "height": display_height,
    }


def main() -> int:
    """CLI entrypoint."""
    if len(sys.argv) not in {2, 4}:
        print("Usage: prepare_sheet_image.py <image_path> [max_width max_height]")
        return 1

    image_path = Path(sys.argv[1])
    max_width = int(sys.argv[2]) if len(sys.argv) == 4 else DEFAULT_MAX_WIDTH
    max_height = int(sys.argv[3]) if len(sys.argv) == 4 else DEFAULT_MAX_HEIGHT

    try:
        result = build_result(image_path, max_width, max_height)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}")
        return 1

    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
