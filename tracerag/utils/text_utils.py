"""Text utility boundary for normalization and formatting-support operations."""

from __future__ import annotations


def normalize_newlines(text: str) -> str:
    """Normalize line endings to Unix-style ``\\n``."""
    return text.replace("\r\n", "\n").replace("\r", "\n")
