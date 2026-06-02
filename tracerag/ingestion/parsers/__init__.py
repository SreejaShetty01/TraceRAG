"""Parser contracts and registry for the ingestion layer."""

from tracerag.ingestion.parsers.base import BaseParser
from tracerag.ingestion.parsers.bootstrap import (
    PHASE2_DEFERRED_EXTENSIONS,
    PHASE2_DISCOVERABLE_EXTENSIONS,
    bootstrap_parser_registry,
    extensions_awaiting_parser_implementation,
    register_parsers,
)
from tracerag.ingestion.parsers.code_parser import PythonParser
from tracerag.ingestion.parsers.json_parser import JSONParser
from tracerag.ingestion.parsers.markdown_parser import MarkdownParser
from tracerag.ingestion.parsers.registry import ParserRegistry
from tracerag.ingestion.parsers.sql_parser import SQLParser

__all__ = [
    "BaseParser",
    "JSONParser",
    "MarkdownParser",
    "ParserRegistry",
    "PythonParser",
    "PHASE2_DEFERRED_EXTENSIONS",
    "PHASE2_DISCOVERABLE_EXTENSIONS",
    "SQLParser",
    "bootstrap_parser_registry",
    "extensions_awaiting_parser_implementation",
    "register_parsers",
]
