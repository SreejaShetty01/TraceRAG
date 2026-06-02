"""Vector storage layer for TraceRAG chunk embeddings."""

from tracerag.db.vector.bootstrap import (
    bootstrap_collection,
    bootstrap_qdrant_collection,
    create_vector_store,
)
from tracerag.db.vector.config import CollectionConfig, QdrantConfig, VectorStoreConfig
from tracerag.db.vector.contracts import VectorStore
from tracerag.db.vector.indexer import (
    create_upsert_pipeline,
    upsert_embedding_batch,
    upsert_embedding_records,
)
from tracerag.db.vector.pipeline import VectorUpsertPipeline
from tracerag.db.vector.qdrant_provider import QdrantVectorStore

__all__ = [
    "CollectionConfig",
    "QdrantConfig",
    "QdrantVectorStore",
    "VectorStore",
    "VectorStoreConfig",
    "VectorUpsertPipeline",
    "bootstrap_collection",
    "bootstrap_qdrant_collection",
    "create_upsert_pipeline",
    "create_vector_store",
    "upsert_embedding_batch",
    "upsert_embedding_records",
]
