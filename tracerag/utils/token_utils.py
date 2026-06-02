"""Token utility boundary for deterministic token counting and size policy checks."""

from __future__ import annotations

# Conservative character-per-token estimate for local chunk sizing (no model tokenizer required).
_CHARS_PER_TOKEN = 4


def estimate_token_count(text: str) -> int:
    """Estimate token count for chunk policy checks.

    Uses a fixed character heuristic suitable for sizing before embedding.
    Replace with a model tokenizer when embedding models are wired in.
    """
    if not text:
        return 0
    return max(1, len(text) // _CHARS_PER_TOKEN)
