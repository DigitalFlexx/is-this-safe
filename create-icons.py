#!/usr/bin/env python3
"""
Generate shield icons for the Is This Safe? extension.
No external dependencies — uses only Python stdlib.
Run from the is-this-safe/ directory: python3 create-icons.py
"""
import os
import struct
import zlib
import math


def make_chunk(chunk_type: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)


def write_png(width: int, height: int, pixels: list) -> bytes:
    """pixels: list of rows, each row a list of (r, g, b) tuples."""
    raw = b""
    for row in pixels:
        raw += b"\x00"          # filter-type: None
        for r, g, b in row:
            raw += bytes([r, g, b])
    return (
        b"\x89PNG\r\n\x1a\n"
        + make_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + make_chunk(b"IDAT", zlib.compress(raw, 9))
        + make_chunk(b"IEND", b"")
    )


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def lerp(a, b, t):
    return int(a + (b - a) * t)


def lerp_color(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def seg_dist(px, py, ax, ay, bx, by):
    """Distance from point (px,py) to segment (ax,ay)→(bx,by)."""
    dx, dy = bx - ax, by - ay
    len2 = dx * dx + dy * dy
    if len2 == 0:
        return math.hypot(px - ax, py - ay)
    t = clamp(((px - ax) * dx + (py - ay) * dy) / len2, 0.0, 1.0)
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def make_icon(size: int) -> list:
    """
    Draws a rounded-square shield in green with a white checkmark.
    Returns a list of pixel rows.
    """
    W, H = size, size
    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0

    # Shield geometry (relative)
    pad      = W * 0.09
    half_w   = W / 2.0 - pad
    half_h   = H / 2.0 - pad
    corner_r = W * 0.17

    # Colours
    WHITE   = (255, 255, 255)
    GREEN_T = (34,  197,  94)   # #22c55e  — top of shield
    GREEN_B = (22,  163,  74)   # #16a34a  — bottom of shield

    # Checkmark arms (normalised 0‥1 inside the icon)
    CHECK_SEGS = [
        ((0.26, 0.53), (0.43, 0.70)),
        ((0.43, 0.70), (0.74, 0.36)),
    ]
    CHECK_PX = max(1.2, W * 0.065)   # half-thickness in pixels

    def in_shield(x, y):
        dx = abs(x - cx)
        dy = abs(y - cy)
        iw = half_w - corner_r
        ih = half_h - corner_r
        if dx <= iw and dy <= ih:
            return True
        if dx <= iw and dy <= half_h:
            return True
        if dy <= ih and dx <= half_w:
            return True
        if dx <= half_w and dy <= half_h:
            return math.hypot(dx - iw, dy - ih) <= corner_r
        return False

    def near_check(x, y):
        if size < 24:
            return False
        px, py = x / W, y / H
        for (ax, ay), (bx, by) in CHECK_SEGS:
            if seg_dist(px, py, ax, ay, bx, by) * W < CHECK_PX:
                return True
        return False

    pixels = []
    for y in range(H):
        row = []
        for x in range(W):
            if in_shield(x, y):
                t = y / max(H - 1, 1)
                base = lerp_color(GREEN_T, GREEN_B, t)
                row.append(WHITE if near_check(x, y) else base)
            else:
                row.append(WHITE)
        pixels.append(row)

    return pixels


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "icons")
    os.makedirs(out_dir, exist_ok=True)

    for size in [16, 32, 48, 128]:
        pix  = make_icon(size)
        data = write_png(size, size, pix)
        path = os.path.join(out_dir, f"{size}.png")
        with open(path, "wb") as f:
            f.write(data)
        print(f"  ✓  icons/{size}.png  ({size}×{size}, {len(data):,} bytes)")

    print("\nAll icons created.")


if __name__ == "__main__":
    main()
