"""Hash utility boundary for content identity and deduplication primitives."""

from __future__ import annotations

import hashlib


def sha256_hex(text: str) -> str:
    """Return the SHA-256 hex digest of UTF-8 encoded text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
