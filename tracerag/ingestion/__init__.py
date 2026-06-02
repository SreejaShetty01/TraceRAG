"""Ingestion layer: discovery, parsing, and document normalization."""

from tracerag.ingestion.filters import DiscoveryFilters
from tracerag.ingestion.parsers.bootstrap import bootstrap_parser_registry
from tracerag.ingestion.validation import (
    classify_extension_phase,
    extension_from_path,
    validate_supported_extension,
    validate_supported_path,
)
from tracerag.ingestion.walker import WorkspaceDiscoveryService

__all__ = [
    "DiscoveryFilters",
    "WorkspaceDiscoveryService",
    "bootstrap_parser_registry",
    "classify_extension_phase",
    "extension_from_path",
    "validate_supported_extension",
    "validate_supported_path",
]
