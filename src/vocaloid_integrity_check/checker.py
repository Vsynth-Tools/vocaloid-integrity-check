"""Core integrity check for Vocaloid voicebank indexes (``.ddi``)."""

import hashlib
import re
import struct

# Vocaloid 2 root tag -> (salt prefix, salt suffix) for the name digest.
SALTS = {
    b"ARR2": ("K2ho", "nF"),
    b"ARR3": ("K2ho", "nF"),
    b"ARR4": ("1m5Pj", "qFE"),
}

V3V4_ROOTS = {b"DBSe"}  # retail V3/V4 library
DEV_ROOTS = {b"DBS "}   # development tree, deliberately unsupported

PHDC_OFFSET = 0x18       # pos(8) + tag(4) + size(4) + flags(8)
V3V4_PHDC_OFFSET = 0x1C  # as above plus a u32 version after the flags
DIGEST_LEN = 32
BLOCK_LEN = 260

VERIFIED = "hash verified"
FAIL = "hash fail"
ABSENT = "hash not present"
UNVERIFIABLE = "hash not verifiable"
UNCHECKED = "hash present, not checkable"


def expected_digest(stem, root):
    """Return the expected digest for *stem* under *root*, or None if unknown."""
    salts = SALTS.get(root)
    if salts is None or not stem.isascii():
        return None
    return hashlib.md5(
        (salts[0] + stem.upper() + salts[1]).encode("ascii")
    ).hexdigest()


def locate_phdc(data, offset=PHDC_OFFSET):
    """Return (offset, size) of the PHDC chunk, or raise ValueError."""
    if len(data) < offset + 8:
        raise ValueError("file too short to contain a voicebank index")
    if data[offset:offset + 4] != b"PHDC":
        raise ValueError(
            f"no PHDC chunk at {hex(offset)}; not a Vocaloid voicebank index"
        )
    size = struct.unpack("<I", data[offset + 4:offset + 8])[0]
    if size < 12 or offset + size > len(data):
        raise ValueError("PHDC size is invalid or runs past end of file")
    return offset, size


def read_digest(data):
    """Return (root, stored digest or None, status note)."""
    root = data[8:12]

    if root in DEV_ROOTS:
        return root, None, "development tree; not supported"
    if root in V3V4_ROOTS:
        off, size = locate_phdc(data, V3V4_PHDC_OFFSET)
        block = data[off + size:off + size + BLOCK_LEN]
        if len(block) < BLOCK_LEN:
            return root, None, "Vocaloid 3/4 hash store is truncated"
        return root, block[:DIGEST_LEN].decode("ascii", "replace"), ""

    off, size = locate_phdc(data)
    if root not in SALTS:
        return root, None, "root has no digest block"
    block = data[off + size:off + size + BLOCK_LEN]
    if len(block) < BLOCK_LEN:
        return root, None, "digest block truncated"
    stored = block[:DIGEST_LEN]
    if not re.fullmatch(rb"[0-9a-f]{32}", stored):
        return root, None, "digest block is not lowercase hex"
    return root, stored.decode("ascii"), ""


def check(data, stem):
    """Check *data* against the bank name *stem* and return a result dict."""
    root, stored, note = read_digest(data)
    root_name = root.decode("ascii", "replace")

    if stored is None:
        return {
            "status": ABSENT,
            "root": root_name,
            "stem": stem,
            "note": note,
            "exit_code": 2,
        }

    # Vocaloid 3/4: the store is present and readable, but it is derived from the
    # licence volume and the voice name, neither of which is recoverable from the
    # index. Report the value; do not judge it.
    if root in V3V4_ROOTS:
        return {
            "status": UNCHECKED,
            "root": root_name,
            "stem": stem,
            "stored": stored,
            "note": "Vocaloid 3/4 store is licence-derived; value reported, not judged",
            "exit_code": 2,
        }

    computed = expected_digest(stem, root)
    if computed is None:
        return {
            "status": UNVERIFIABLE,
            "root": root_name,
            "stem": stem,
            "stored": stored,
            "note": "non-ASCII name: expected digest depends on engine locale",
            "exit_code": 2,
        }
    ok = computed == stored
    return {
        "status": VERIFIED if ok else FAIL,
        "root": root_name,
        "stem": stem,
        "stored": stored,
        "computed": computed,
        "note": "" if ok else "digest does not match this name",
        "exit_code": 0 if ok else 1,
    }
