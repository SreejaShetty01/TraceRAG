"""Supported-extension validation helpers for ingestion discovery."""

from __future__ import annotations

from pathlib import Path

from tracerag.core.exceptions import UnsupportedFileTypeError
from tracerag.models.types import (
    DEFERRED_EXTENSIONS,
    DISCOVERABLE_EXTENSIONS,
    SUPPORTED_EXTENSIONS,
    FileExtension,
    normalize_extension,
)


def extension_from_path(path: Path) -> FileExtension:
    """Extract and normalize the extension from a filesystem path."""
    return normalize_extension(path.suffix)


def validate_supported_extension(extension: str, *, path: Path | None = None) -> FileExtension:
    """Return a normalized extension or raise ``UnsupportedFileTypeError``."""
    normalized = normalize_extension(extension)
    if normalized not in SUPPORTED_EXTENSIONS:
        path_str = str(path) if path is not None else None
        raise UnsupportedFileTypeError(normalized, path_str)
    return normalized


def validate_supported_path(path: Path) -> FileExtension:
    """Validate that ``path`` has a supported extension."""
    return validate_supported_extension(path.suffix, path=path)


def classify_extension_phase(extension: FileExtension) -> str:
    """Return a phase label: ``discoverable``, ``deferred``, or ``unsupported``."""
    if extension in DISCOVERABLE_EXTENSIONS:
        return "discoverable"
    if extension in DEFERRED_EXTENSIONS:
        return "deferred"
    if extension in SUPPORTED_EXTENSIONS:
        return "supported"
    return "unsupported"
