#!/usr/bin/env python3
"""Write a minimal valid PNG (1x1 gray pixel) to the given path. No deps beyond stdlib."""
import struct
import zlib
import sys
import os


def make_png(path):
    # PNG signature
    sig = b"\x89PNG\r\n\x1a\n"
    # IHDR: 1x1, 8-bit grayscale
    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 0, 0, 0, 0)
    ihdr_crc = struct.pack(">I", zlib.crc32(b"IHDR" + ihdr_data) & 0xFFFFFFFF)
    ihdr = struct.pack(">I", 13) + b"IHDR" + ihdr_data + ihdr_crc
    # IDAT: raw byte 0x00 (gray 0), filter byte 0, then compress
    raw = b"\x00\x00"  # filter 0, then one pixel value 0
    compressed = zlib.compress(raw, 9)
    idat_crc = struct.pack(">I", zlib.crc32(b"IDAT" + compressed) & 0xFFFFFFFF)
    idat = struct.pack(">I", len(compressed)) + b"IDAT" + compressed + idat_crc
    # IEND
    iend_crc = struct.pack(">I", zlib.crc32(b"IEND") & 0xFFFFFFFF)
    iend = struct.pack(">I", 0) + b"IEND" + iend_crc
    png = sig + ihdr + idat + iend
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for name in ["workspace/src_images/placeholder.png", "workspace/dst_images/placeholder.png"]:
            make_png(os.path.join(root, name))
            print("Created", name)
    else:
        make_png(sys.argv[1])
        print("Created", sys.argv[1])
