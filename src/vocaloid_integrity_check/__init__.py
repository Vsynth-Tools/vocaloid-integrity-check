"""Vocaloid integrity checker.

Locates and, where the scheme is known, verifies the name digest stored in a
Vocaloid voicebank index (``.ddi``).
"""

from .checker import (
    ABSENT,
    BLOCK_LEN,
    DIGEST_LEN,
    FAIL,
    PHDC_OFFSET,
    SALTS,
    UNCHECKED,
    UNVERIFIABLE,
    V3V4_PHDC_OFFSET,
    VERIFIED,
    check,
    expected_digest,
    locate_phdc,
    read_digest,
)

__version__ = "1.0.0"

__all__ = [
    "check",
    "expected_digest",
    "locate_phdc",
    "read_digest",
    "SALTS",
    "PHDC_OFFSET",
    "V3V4_PHDC_OFFSET",
    "BLOCK_LEN",
    "DIGEST_LEN",
    "VERIFIED",
    "FAIL",
    "ABSENT",
    "UNVERIFIABLE",
    "UNCHECKED",
    "__version__",
]
