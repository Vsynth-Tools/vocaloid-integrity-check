#!/usr/bin/env python3
"""Checks for the Vocaloid integrity checker. Run: python tests/test_checker.py

These are development checks, not part of the installed package.
"""

import hashlib
import os
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, "src"))

from vocaloid_integrity_check import check, SALTS, PHDC_OFFSET  # noqa: E402

FAILURES = []


def build(root, name=None, body=64, digest_hex=None):
    """Synthetic index: real layout, so the parser under test is the real one."""
    header = bytearray(PHDC_OFFSET)
    header[8:12] = root
    data = bytes(header) + b"PHDC" + struct.pack("<I", body) + b"\x00" * (body - 8)
    if name is None and digest_hex is None:
        return data
    if digest_hex is None:
        salts = SALTS[root]
        digest_hex = hashlib.md5((salts[0] + name.upper() + salts[1]).encode()).hexdigest()
    return data + digest_hex.encode() + b"\x00" * (BLOCK_LEN - 32)


def expect(label, data, stem, want):
    got = check(data, stem)
    if got["status"] != want:
        FAILURES.append(f"{label}: expected {want!r}, got {got['status']!r}")
        print(f'  FAIL  {label:28s} {got["status"]}')
    else:
        print(f'  ok    {label:28s} {got["status"]}')
    return got


BLOCK_LEN = 260

# --- Vocaloid 2 -----------------------------------------------------------
expect("exact name", build(b"ARR4", "Yuki"), "Yuki", "hash verified")
expect("case-insensitive", build(b"ARR4", "Yuki"), "yUkI", "hash verified")
expect("wrong name", build(b"ARR4", "Yuki"), "Kiyoteru", "hash fail")
expect("renamed pair", build(b"ARR4", "Yukari"), "Mickey", "hash fail")
expect("arr2 root", build(b"ARR2", "Rin"), "Rin", "hash verified")
expect("arr3 root (predicted)", build(b"ARR3", "Gackpoid"), "Gackpoid", "hash verified")
expect("empty digest field", build(b"ARR4", digest_hex="0" * 32), "Yuki", "hash fail")
expect("legacy ARR root", build(b"ARR ", None), "miku", "hash not present")
expect("truncated block", build(b"ARR4", "Yuki")[: PHDC_OFFSET + 64 + 100], "Yuki",
       "hash not present")
expect("non-ASCII name", build(b"ARR4", "Yuki"), "Yuki\u4f53\u9a13", "hash not verifiable")

# --- Vocaloid 3 / 4 -------------------------------------------------------
expect("dev tree root", build(b"DBS ", None), "Sachiko", "hash not present")


def build_v34(store_hex, body=64):
    """Vocaloid 3/4 layout: same header plus a u32 version, so PHDC sits 4 bytes later."""
    header = bytearray(0x1C)
    header[8:12] = b"DBSe"
    return (
        bytes(header)
        + b"PHDC"
        + struct.pack("<I", body)
        + b"\x00" * (body - 8)
        + store_hex.encode()
        + b"\x00" * (BLOCK_LEN - 32)
    )


# Real values from shipped Vocaloid 3 and 4 libraries; reported, never judged.
for name, value in (
    ("GACHAPOID_V3", "acfb2575a3e54db67d356b12eab88c6e"),
    ("Matcha", "cdd787ab1039a67267dcb3d4a9e57cb9"),
    ("Yukari_Onn", "086b8475993c403412e57753bbfe8f41"),
):
    got = check(build_v34(value), name)
    if got["status"] != "hash present, not checkable" or got.get("stored") != value:
        FAILURES.append(f"v3/v4 {name}: {got}")
        print(f"  FAIL  v3/v4 {name}")
    else:
        print(f"  ok    v3/v4 {name:14s} store located, not judged")

trunc = build_v34("cdd787ab1039a67267dcb3d4a9e57cb9")[: 0x1C + 64 + 100]
expect("v4 truncated store", trunc, "Matcha", "hash not present")

# --- real published values -------------------------------------------------
# Digests taken from shipped Vocaloid 2 banks; proves the salts, not just the plumbing.
for name, want in (
    ("Yuki", "92942a5a960cdf938b3d742d8a75f5df"),
    ("Rin", "b9020f7a8acdba0c3e649313ae4bb704"),
):
    root = b"ARR2" if name == "Rin" else b"ARR4"
    got = check(build(root, name), name)
    if got.get("stored") != want:
        FAILURES.append(f'real digest {name}: expected {want}, got {got.get("stored")}')
        print(f"  FAIL  real digest {name}")
    else:
        print(f"  ok    real digest {name:16s} {want}")

# --- error handling --------------------------------------------------------
for label, data in (("empty file", b""), ("not a ddi", b"\xff" * 64)):
    try:
        check(data, "x")
        FAILURES.append(f"{label}: no exception raised")
        print(f"  FAIL  {label:28s} no exception")
    except ValueError:
        print(f"  ok    {label:28s} ValueError")

# --- CLI smoke test --------------------------------------------------------
with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, "X.ddi")
    with open(p, "wb") as f:
        f.write(build(b"ARR4", "X"))
    for args, want_code in (
        (["--ddb", "X.ddb"], 0),
        (["--ddb", "Y.ddb"], 1),
        (["--json"], 0),
    ):
        r = subprocess.run(
            [sys.executable, "-m", "vocaloid_integrity_check"] + [p] + args,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": os.path.join(os.path.dirname(__file__),
                                                          os.pardir, "src")},
        )
        if r.returncode != want_code:
            FAILURES.append(f'cli {args}: exit {r.returncode} != {want_code} ({r.stderr[:80]})')
            print(f"  FAIL  cli {args}")
        else:
            print(f'  ok    cli {" ".join(args):28s} exit {r.returncode}')

print()
if FAILURES:
    print(f"{len(FAILURES)} failure(s):")
    for f in FAILURES:
        print("  -", f)
    sys.exit(1)
print("all checks passed")
