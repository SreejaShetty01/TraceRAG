"""Abstract parser contracts defining normalization responsibilities for source artifacts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from tracerag.models.document import ParsedDocument
from tracerag.models.types import FileExtension, ParserName


class BaseParser(ABC):
    """Contract for format-specific parsers that emit ``ParsedDocument`` instances."""

    @property
    @abstractmethod
    def name(self) -> ParserName:
        """Stable parser identifier used in provenance metadata."""

    @property
    @abstractmethod
    def supported_extensions(self) -> frozenset[FileExtension]:
        """File extensions this parser handles (lowercase, with leading dot)."""

    def supports(self, path: Path) -> bool:
        """Return whether ``path`` has an extension handled by this parser."""
        return path.suffix.lower() in self.supported_extensions

    @abstractmethod
    def parse(
        self,
        path: Path,
        *,
        workspace_root: Path | None = None,
    ) -> ParsedDocument:
        """Normalize a source artifact at ``path`` into a ``ParsedDocument``.

        Implementations are responsible for reading the file, building
        ``DocumentMetadata``, and populating ``content`` (and optional ``blocks``).
        """
