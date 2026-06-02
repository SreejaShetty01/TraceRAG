"""Vector datastore client boundary for provider-specific access coordination."""

from __future__ import annotations

from tracerag.db.vector.bootstrap import bootstrap_collection, create_vector_store
from tracerag.db.vector.config import VectorStoreConfig
from tracerag.db.vector.contracts import VectorStore

__all__ = [
    "VectorStore",
    "VectorStoreConfig",
    "bootstrap_collection",
    "create_vector_store",
]
