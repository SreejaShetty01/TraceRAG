"""Parser selection registry mapping file types to parser boundaries."""

from __future__ import annotations

from pathlib import Path

from tracerag.core.exceptions import (
    ParserNotFoundError,
    ParserRegistrationError,
    UnsupportedFileTypeError,
)
from tracerag.ingestion.parsers.base import BaseParser
from tracerag.models.types import (
    SUPPORTED_EXTENSIONS,
    FileExtension,
    ParserName,
    normalize_extension,
)


class ParserRegistry:
    """Registry that resolves source paths to registered ``BaseParser`` instances."""

    def __init__(self) -> None:
        self._by_extension: dict[FileExtension, BaseParser] = {}
        self._parsers: dict[ParserName, BaseParser] = {}

    @property
    def registered_extensions(self) -> frozenset[FileExtension]:
        """Extensions with an assigned parser."""
        return frozenset(self._by_extension)

    @property
    def parser_names(self) -> frozenset[ParserName]:
        """Names of all registered parsers."""
        return frozenset(self._parsers)

    def register(self, parser: BaseParser) -> None:
        """Register a parser and bind each of its supported extensions."""
        if parser.name in self._parsers:
            msg = f"Parser {parser.name!r} is already registered"
            raise ParserRegistrationError(msg)

        if not parser.supported_extensions:
            msg = f"Parser {parser.name!r} declares no supported_extensions"
            raise ParserRegistrationError(msg)

        for extension in parser.supported_extensions:
            normalized = normalize_extension(extension)
            if normalized not in SUPPORTED_EXTENSIONS:
                msg = (
                    f"Extension {normalized!r} is not in the TraceRAG supported "
                    f"vocabulary for parser {parser.name!r}"
                )
                raise ParserRegistrationError(msg)
            existing = self._by_extension.get(normalized)
            if existing is not None:
                msg = (
                    f"Extension {normalized!r} is already bound to parser "
                    f"{existing.name!r}; cannot register {parser.name!r}"
                )
                raise ParserRegistrationError(msg)
            self._by_extension[normalized] = parser

        self._parsers[parser.name] = parser

    def resolve(self, path: Path) -> BaseParser:
        """Return the parser registered for ``path``'s extension."""
        resolved = path.expanduser().resolve()
        extension = normalize_extension(resolved.suffix)

        if extension not in SUPPORTED_EXTENSIONS:
            raise UnsupportedFileTypeError(extension, str(resolved))

        try:
            return self._by_extension[extension]
        except KeyError as exc:
            raise ParserNotFoundError(extension, str(resolved)) from exc

    def get(self, name: ParserName) -> BaseParser | None:
        """Return a parser by name, or ``None`` if not registered."""
        return self._parsers.get(name)
