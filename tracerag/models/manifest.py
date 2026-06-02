"""Ingestion manifest contracts produced by workspace discovery."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from tracerag.models.types import (
    DISCOVERABLE_EXTENSIONS,
    DEFERRED_EXTENSIONS,
    DiscoveryStatus,
    FileExtension,
    ParserName,
    SourceKind,
    normalize_extension,
    source_kind_for_extension,
)


class ManifestEntry(BaseModel):
    """A single file discovered within a workspace and classified for ingestion."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid", arbitrary_types_allowed=True)

    file_path: Path
    relative_path: Path
    file_extension: FileExtension
    source_kind: SourceKind
    status: DiscoveryStatus
    file_size_bytes: int = Field(ge=0)
    parser_name: ParserName | None = None
    skip_reason: str | None = None

    @field_validator("file_path", "relative_path", mode="before")
    @classmethod
    def _coerce_path(cls, value: object) -> Path:
        if isinstance(value, Path):
            return value
        if isinstance(value, str):
            return Path(value)
        msg = "path fields must be str or Path"
        raise TypeError(msg)

    @field_validator("file_extension", mode="before")
    @classmethod
    def _normalize_extension(cls, value: str) -> FileExtension:
        return normalize_extension(value)


class IngestionManifest(BaseModel):
    """Aggregate discovery result for a workspace root."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid", arbitrary_types_allowed=True)

    workspace_root: Path
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    entries: tuple[ManifestEntry, ...] = ()

    @field_validator("workspace_root", mode="before")
    @classmethod
    def _coerce_workspace(cls, value: object) -> Path:
        if isinstance(value, Path):
            return value
        if isinstance(value, str):
            return Path(value)
        msg = "workspace_root must be str or Path"
        raise TypeError(msg)

    @field_validator("workspace_root", mode="after")
    @classmethod
    def _resolve_workspace(cls, value: Path) -> Path:
        return value.expanduser().resolve()

    @field_validator("discovered_at", mode="after")
    @classmethod
    def _ensure_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_files(self) -> int:
        return len(self.entries)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ready_count(self) -> int:
        return sum(1 for entry in self.entries if entry.status == DiscoveryStatus.READY)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def pending_parser_count(self) -> int:
        return sum(1 for entry in self.entries if entry.status == DiscoveryStatus.PENDING_PARSER)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def deferred_count(self) -> int:
        return sum(1 for entry in self.entries if entry.status == DiscoveryStatus.DEFERRED)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def skipped_count(self) -> int:
        return sum(1 for entry in self.entries if entry.status == DiscoveryStatus.SKIPPED)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def unsupported_count(self) -> int:
        return sum(1 for entry in self.entries if entry.status == DiscoveryStatus.UNSUPPORTED)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ingestible_entries(self) -> tuple[ManifestEntry, ...]:
        """Entries prepared for parsing in the active discovery phase."""
        return tuple(
            entry
            for entry in self.entries
            if entry.status in {DiscoveryStatus.READY, DiscoveryStatus.PENDING_PARSER}
            and entry.file_extension in DISCOVERABLE_EXTENSIONS
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def deferred_entries(self) -> tuple[ManifestEntry, ...]:
        return tuple(entry for entry in self.entries if entry.status == DiscoveryStatus.DEFERRED)
