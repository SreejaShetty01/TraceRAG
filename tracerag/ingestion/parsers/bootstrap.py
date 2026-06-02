"""Parser registry bootstrap for ingestion discovery and pipeline wiring."""

from __future__ import annotations

from tracerag.ingestion.parsers.code_parser import PythonParser
from tracerag.ingestion.parsers.json_parser import JSONParser
from tracerag.ingestion.parsers.markdown_parser import MarkdownParser
from tracerag.ingestion.parsers.registry import ParserRegistry
from tracerag.ingestion.parsers.sql_parser import SQLParser
from tracerag.models.types import (
    DEFERRED_EXTENSIONS,
    DISCOVERABLE_EXTENSIONS,
    FileExtension,
)

PHASE2_DISCOVERABLE_EXTENSIONS: frozenset[FileExtension] = DISCOVERABLE_EXTENSIONS
PHASE2_DEFERRED_EXTENSIONS: frozenset[FileExtension] = DEFERRED_EXTENSIONS

_PHASE3_PARSERS = (
    MarkdownParser,
    JSONParser,
    PythonParser,
    SQLParser,
)


def bootstrap_parser_registry(*, register_all: bool = True) -> ParserRegistry:
    """Create a parser registry with Phase 3 parser implementations registered."""
    registry = ParserRegistry()
    if register_all:
        register_parsers(registry)
    return registry


def register_parsers(registry: ParserRegistry) -> None:
    """Register all built-in Phase 3 parsers on ``registry``."""
    for parser_cls in _PHASE3_PARSERS:
        registry.register(parser_cls())


def extensions_awaiting_parser_implementation(
    registry: ParserRegistry | None = None,
) -> frozenset[FileExtension]:
    """Return discoverable extensions not yet bound to a parser."""
    reg = registry or bootstrap_parser_registry()
    return DISCOVERABLE_EXTENSIONS - reg.registered_extensions
