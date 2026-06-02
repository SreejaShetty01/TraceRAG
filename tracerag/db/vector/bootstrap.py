"""Collection bootstrap utilities for vector storage."""

from __future__ import annotations

from tracerag.db.vector.config import CollectionConfig, QdrantConfig, VectorStoreConfig
from tracerag.db.vector.contracts import VectorStore
from tracerag.db.vector.qdrant_provider import QdrantVectorStore


def create_vector_store(config: VectorStoreConfig | None = None) -> VectorStore:
    """Create the default vector store (Qdrant)."""
    policy = config or VectorStoreConfig.default()
    if policy.provider == "qdrant":
        return QdrantVectorStore(policy.qdrant)
    msg = f"unsupported vector store provider: {policy.provider!r}"
    raise ValueError(msg)


def bootstrap_collection(
    store: VectorStore | None = None,
    *,
    config: VectorStoreConfig | None = None,
    collection: CollectionConfig | None = None,
) -> VectorStore:
    """Ensure the vector collection exists and return the store instance."""
    policy = config or VectorStoreConfig.default()
    vector_store = store or create_vector_store(policy)
    vector_store.bootstrap_collection(collection or policy.qdrant.collection)
    return vector_store


def bootstrap_qdrant_collection(
    qdrant_config: QdrantConfig | None = None,
    *,
    collection: CollectionConfig | None = None,
) -> QdrantVectorStore:
    """Bootstrap a Qdrant collection and return the connected store."""
    config = qdrant_config or QdrantConfig.default()
    store = QdrantVectorStore(config)
    store.bootstrap_collection(collection or config.collection)
    return store
