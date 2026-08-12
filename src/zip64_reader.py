"""Streaming reader for ZIP members, including Deflate64 (method 9).

The game2 archive stores 7 of its 8 parts with Deflate64, which CPython's
`zipfile` refuses to open ("That compression method is not supported").
Rather than requiring a 7-Zip install, this module seeks to the member's local
header, streams the raw compressed bytes, and inflates them incrementally with
the `inflate64` extension. Memory stays flat regardless of member size, which
matters here because the parts expand to ~520 MB each.

Standard Deflate (method 8) and Stored (method 0) are handled too, so callers
can use one code path for every member.
"""

from __future__ import annotations

import struct
import zipfile
import zlib
from collections.abc import Iterator
from pathlib import Path

import inflate64

_LOCAL_HEADER = struct.Struct("<IHHHHHIIIHH")
_LOCAL_SIG = 0x04034B50
CHUNK = 1 << 20  # 1 MiB of compressed input per read

STORED, DEFLATED, DEFLATE64 = 0, 8, 9


def _data_offset(fh, header_offset: int) -> int:
    """Return the absolute offset of a member's compressed payload."""
    fh.seek(header_offset)
    raw = fh.read(_LOCAL_HEADER.size)
    if len(raw) < _LOCAL_HEADER.size:
        raise ValueError("Truncated local file header")

    sig, _, _, _, _, _, _, _, _, name_len, extra_len = _LOCAL_HEADER.unpack(raw)
    if sig != _LOCAL_SIG:
        raise ValueError(f"Bad local header signature 0x{sig:08X}")

    # Name/extra lengths in the LOCAL header may differ from the central
    # directory's, so they must be read from here rather than from ZipInfo.
    return header_offset + _LOCAL_HEADER.size + name_len + extra_len


def iter_member_chunks(zip_path: str | Path, name: str,
                       chunk: int = CHUNK) -> Iterator[bytes]:
    """Yield decompressed chunks of one archive member."""
    zip_path = Path(zip_path)

    with zipfile.ZipFile(zip_path) as zf:
        info = zf.getinfo(name)

    method = info.compress_type
    if method not in (STORED, DEFLATED, DEFLATE64):
        raise NotImplementedError(f"Unsupported compression method {method}")

    with open(zip_path, "rb") as fh:
        fh.seek(_data_offset(fh, info.header_offset))
        remaining = info.compress_size

        if method == STORED:
            while remaining > 0:
                data = fh.read(min(chunk, remaining))
                if not data:
                    break
                remaining -= len(data)
                yield data
            return

        # -15 selects a raw stream with no zlib wrapper, matching ZIP framing.
        dec = zlib.decompressobj(-15) if method == DEFLATED else inflate64.Inflater()

        while remaining > 0:
            data = fh.read(min(chunk, remaining))
            if not data:
                break
            remaining -= len(data)
            out = dec.decompress(data) if method == DEFLATED else dec.inflate(data)
            if out:
                yield out

        if method == DEFLATED:
            tail = dec.flush()
            if tail:
                yield tail


def iter_member_lines(zip_path: str | Path, name: str,
                      chunk: int = CHUNK) -> Iterator[bytes]:
    """Yield newline-delimited records from one archive member.

    Splits on b"\\n" across chunk boundaries so records are never truncated.
    """
    buf = b""
    for block in iter_member_chunks(zip_path, name, chunk):
        buf += block
        if b"\n" not in buf:
            continue
        *lines, buf = buf.split(b"\n")
        yield from lines
    if buf:
        yield buf
