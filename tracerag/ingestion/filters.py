"""File and directory filtering rules applied during workspace discovery."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from tracerag.models.types import FileExtension
from tracerag.utils.file_utils import is_hidden_name, is_hidden_path

DEFAULT_SKIP_DIR_NAMES: frozenset[str] = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        ".venv",
        "venv",
        "env",
        ".tox",
        "dist",
        "build",
        ".eggs",
        "htmlcov",
        ".idea",
        ".vscode",
        "logs",
    }
)

DEFAULT_SKIP_FILE_NAMES: frozenset[str] = frozenset(
    {
        ".DS_Store",
        "Thumbs.db",
        "desktop.ini",
    }
)


class DiscoveryFilters(BaseModel):
    """Configurable rules that constrain recursive workspace traversal."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    skip_dir_names: frozenset[str] = Field(default=DEFAULT_SKIP_DIR_NAMES)
    skip_file_names: frozenset[str] = Field(default=DEFAULT_SKIP_FILE_NAMES)
    skip_extensions: frozenset[FileExtension] = Field(default_factory=frozenset)
    include_hidden: bool = False
    include_unsupported_files: bool = False
    include_deferred_files: bool = True
    max_file_size_bytes: int | None = Field(default=None, ge=1)

    @classmethod
    def default(cls) -> DiscoveryFilters:
        """Return production-default discovery filters."""
        return cls()

    def should_skip_dir(self, directory: Path) -> bool:
        """Return whether a directory should be excluded from traversal."""
        name = directory.name
        if name in self.skip_dir_names:
            return True
        if name.endswith(".egg-info"):
            return True
        if not self.include_hidden and is_hidden_name(name):
            return True
        return False

    def should_skip_file(self, file_path: Path) -> str | None:
        """Return a skip reason string, or ``None`` if the file may be considered."""
        name = file_path.name
        if name in self.skip_file_names:
            return f"excluded filename: {name!r}"
        if not self.include_hidden and is_hidden_path(file_path):
            return "hidden path"
        extension = file_path.suffix.lower()
        if extension and extension in self.skip_extensions:
            return f"excluded extension: {extension!r}"
        if self.max_file_size_bytes is not None:
            try:
                size = file_path.stat().st_size
            except OSError:
                return "unreadable file metadata"
            if size > self.max_file_size_bytes:
                return f"file exceeds max size ({size} > {self.max_file_size_bytes})"
        return None
