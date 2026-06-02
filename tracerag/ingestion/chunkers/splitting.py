"""Text splitting helpers for token-bounded child chunk generation."""

from __future__ import annotations

from tracerag.ingestion.chunkers.config import ChunkingConfig
from tracerag.utils.token_utils import estimate_token_count

_CHARS_PER_TOKEN = 4


def _token_window_chars(token_limit: int) -> int:
    return token_limit * _CHARS_PER_TOKEN


def split_into_child_chunks(text: str, config: ChunkingConfig) -> list[str]:
    """Split ``text`` into child-sized segments with optional overlap."""
    normalized = text.strip()
    if not normalized:
        return []

    if estimate_token_count(normalized) <= config.child_token_max:
        return [normalized]

    max_chars = _token_window_chars(config.child_token_max)
    overlap_chars = _token_window_chars(config.overlap_tokens)
    chunks: list[str] = []
    start = 0

    while start < len(normalized):
        end = min(len(normalized), start + max_chars)
        window = normalized[start:end]

        if end < len(normalized):
            newline_break = window.rfind("\n")
            if newline_break > max_chars // 2:
                end = start + newline_break + 1
                window = normalized[start:end]

        piece = window.strip()
        if piece:
            chunks.append(piece)
        if end >= len(normalized):
            break
        start = max(start + 1, end - overlap_chars)

    return chunks
