"""Hybrid retrieval layer for TraceRAG."""

from tracerag.retrieval.config import RetrievalConfig
from tracerag.retrieval.contracts import DenseRetrievalProvider, SparseRetrievalProvider
from tracerag.retrieval.dense import QdrantDenseRetriever
from tracerag.retrieval.fusion import fuse_retrieval_results, reciprocal_rank_fusion
from tracerag.retrieval.pipeline import HybridRetrievalPipeline
from tracerag.retrieval.reranker import CrossEncoderReranker
from tracerag.retrieval.sparse import BM25SparseRetriever

__all__ = [
    "BM25SparseRetriever",
    "CrossEncoderReranker",
    "DenseRetrievalProvider",
    "HybridRetrievalPipeline",
    "QdrantDenseRetriever",
    "RetrievalConfig",
    "SparseRetrievalProvider",
    "fuse_retrieval_results",
    "reciprocal_rank_fusion",
]
