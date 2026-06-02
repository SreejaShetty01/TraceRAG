"""Workspace traversal boundary for file discovery with extension and directory filtering."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

from tracerag.core.exceptions import (
    WorkspaceNotADirectoryError,
    WorkspaceNotFoundError,
    WorkspacePermissionError,
)
from tracerag.ingestion.filters import DiscoveryFilters
from tracerag.ingestion.parsers.bootstrap import bootstrap_parser_registry
from tracerag.ingestion.parsers.registry import ParserRegistry
from tracerag.ingestion.validation import extension_from_path
from tracerag.models.manifest import IngestionManifest, ManifestEntry
from tracerag.models.types import (
    DEFERRED_EXTENSIONS,
    DISCOVERABLE_EXTENSIONS,
    SUPPORTED_EXTENSIONS,
    DiscoveryStatus,
    FileExtension,
    SourceKind,
    source_kind_for_extension,
)
from tracerag.utils.file_utils import relative_to_workspace, resolve_workspace_root


class WorkspaceDiscoveryService:
    """Recursively discover, filter, and classify files under a workspace root."""

    def __init__(
        self,
        *,
        filters: DiscoveryFilters | None = None,
        registry: ParserRegistry | None = None,
    ) -> None:
        self._filters = filters or DiscoveryFilters.default()
        self._registry = registry or bootstrap_parser_registry()

    @property
    def filters(self) -> DiscoveryFilters:
        return self._filters

    @property
    def registry(self) -> ParserRegistry:
        return self._registry

    def discover(self, workspace_root: Path | str) -> IngestionManifest:
        """Walk ``workspace_root`` and return a classified ingestion manifest."""
        root = self._validate_workspace(workspace_root)
        entries: list[ManifestEntry] = []

        for file_path in self._iter_files(root):
            entry = self._classify_file(file_path, root)
            if entry is not None:
                entries.append(entry)

        entries.sort(key=lambda item: str(item.relative_path).lower())
        return IngestionManifest(
            workspace_root=root,
            discovered_at=datetime.now(timezone.utc),
            entries=tuple(entries),
        )

    def _validate_workspace(self, workspace_root: Path | str) -> Path:
        root = resolve_workspace_root(workspace_root)
        if not root.exists():
            raise WorkspaceNotFoundError(str(root))
        if not root.is_dir():
            raise WorkspaceNotADirectoryError(str(root))
        return root

    def _iter_files(self, workspace_root: Path) -> Iterator[Path]:
        """Depth-first traversal with directory pruning via filter rules."""
        stack: list[Path] = [workspace_root]
        while stack:
            current = stack.pop()
            try:
                children = sorted(current.iterdir(), key=lambda p: p.name.lower())
            except PermissionError as exc:
                if current == workspace_root:
                    raise WorkspacePermissionError(str(workspace_root), cause=exc) from exc
                continue
            except OSError:
                continue

            for child in reversed(children):
                if child.is_dir():
                    if self._filters.should_skip_dir(child):
                        continue
                    stack.append(child)
                elif child.is_file():
                    yield child.resolve()

    def _classify_file(self, file_path: Path, workspace_root: Path) -> ManifestEntry | None:
        relative = relative_to_workspace(file_path, workspace_root)
        skip_reason = self._filters.should_skip_file(file_path)

        if skip_reason is not None:
            extension = extension_from_path(file_path) if file_path.suffix else ""
            return self._build_entry(
                file_path=file_path,
                relative_path=relative,
                extension=extension,
                status=DiscoveryStatus.SKIPPED,
                skip_reason=skip_reason,
            )

        if not file_path.suffix:
            if self._filters.include_unsupported_files:
                return self._build_entry(
                    file_path=file_path,
                    relative_path=relative,
                    extension="",
                    status=DiscoveryStatus.UNSUPPORTED,
                    skip_reason="no file extension",
                )
            return None

        extension = extension_from_path(file_path)

        if extension not in SUPPORTED_EXTENSIONS:
            if not self._filters.include_unsupported_files:
                return None
            return self._build_entry(
                file_path=file_path,
                relative_path=relative,
                extension=extension,
                status=DiscoveryStatus.UNSUPPORTED,
                skip_reason="extension not in supported vocabulary",
            )

        if extension in DEFERRED_EXTENSIONS:
            if not self._filters.include_deferred_files:
                return None
            return self._build_entry(
                file_path=file_path,
                relative_path=relative,
                extension=extension,
                status=DiscoveryStatus.DEFERRED,
                skip_reason="deferred to a later ingestion phase",
            )

        if extension in DISCOVERABLE_EXTENSIONS:
            if extension in self._registry.registered_extensions:
                parser = self._registry.resolve(file_path)
                return self._build_entry(
                    file_path=file_path,
                    relative_path=relative,
                    extension=extension,
                    status=DiscoveryStatus.READY,
                    parser_name=parser.name,
                )
            return self._build_entry(
                file_path=file_path,
                relative_path=relative,
                extension=extension,
                status=DiscoveryStatus.PENDING_PARSER,
            )

        if self._filters.include_unsupported_files:
            return self._build_entry(
                file_path=file_path,
                relative_path=relative,
                extension=extension,
                status=DiscoveryStatus.UNSUPPORTED,
            )
        return None

    def _build_entry(
        self,
        *,
        file_path: Path,
        relative_path: Path,
        extension: FileExtension,
        status: DiscoveryStatus,
        parser_name: str | None = None,
        skip_reason: str | None = None,
    ) -> ManifestEntry:
        try:
            file_size = file_path.stat().st_size
        except OSError:
            file_size = 0

        kind = source_kind_for_extension(extension) if extension else SourceKind.UNKNOWN

        return ManifestEntry(
            file_path=file_path,
            relative_path=relative_path,
            file_extension=extension,
            source_kind=kind,
            status=status,
            file_size_bytes=file_size,
            parser_name=parser_name,
            skip_reason=skip_reason,
        )
