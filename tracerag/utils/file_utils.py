"""File utility boundary for path normalization and extension classification helpers."""

from __future__ import annotations

from pathlib import Path


def resolve_path(path: Path | str) -> Path:
    """Return an absolute, user-expanded path."""
    return Path(path).expanduser().resolve()


def resolve_workspace_root(path: Path | str) -> Path:
    """Resolve and validate format for a workspace root path."""
    return resolve_path(path)


def relative_to_workspace(file_path: Path, workspace_root: Path) -> Path:
    """Return ``file_path`` relative to ``workspace_root``."""
    return file_path.resolve().relative_to(workspace_root.resolve())


def is_hidden_name(name: str) -> bool:
    """Return whether a file or directory name is hidden (dot-prefixed)."""
    return name.startswith(".")


def is_hidden_path(path: Path) -> bool:
    """Return whether any component of ``path`` is hidden."""
    return any(is_hidden_name(part) for part in path.parts)
