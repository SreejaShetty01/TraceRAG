"""Result-fusion boundary for combining ranked retrieval streams."""

from __future__ import annotations

from tracerag.models.retrieval import RetrievalCandidate, RetrievalQuery, RetrievalResult, RetrievalSource
from tracerag.retrieval.config import RetrievalConfig


def reciprocal_rank_fusion(
    ranked_lists: list[list[RetrievalCandidate]],
    *,
    k: int,
    top_k: int,
    query: RetrievalQuery,
) -> RetrievalResult:
    """Fuse multiple ranked lists using Reciprocal Rank Fusion (RRF).

    Score for each chunk: ``sum(1 / (k + rank_i))`` across all lists.
    """
    scores: dict[str, float] = {}
    by_chunk: dict[str, RetrievalCandidate] = {}

    for ranked in ranked_lists:
        for candidate in ranked:
            chunk_id = candidate.chunk_id
            scores[chunk_id] = scores.get(chunk_id, 0.0) + (1.0 / (k + candidate.rank))
            existing = by_chunk.get(chunk_id)
            if existing is None:
                by_chunk[chunk_id] = candidate
            else:
                by_chunk[chunk_id] = _merge_candidate_metadata(existing, candidate)

    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]

    fused: list[RetrievalCandidate] = []
    for rank, (chunk_id, rrf_score) in enumerate(ordered, start=1):
        base = by_chunk[chunk_id]
        fused.append(
            RetrievalCandidate(
                chunk_id=chunk_id,
                rank=rank,
                score=rrf_score,
                source=RetrievalSource.FUSED,
                point_id=base.point_id,
                payload=base.payload,
                snippet=base.snippet,
                dense_score=base.dense_score,
                sparse_score=base.sparse_score,
                rrf_score=rrf_score,
            )
        )

    return RetrievalResult(query=query, source=RetrievalSource.FUSED, candidates=tuple(fused))


def _merge_candidate_metadata(
    left: RetrievalCandidate,
    right: RetrievalCandidate,
) -> RetrievalCandidate:
    return RetrievalCandidate(
        chunk_id=left.chunk_id,
        rank=min(left.rank, right.rank),
        score=max(left.score, right.score),
        source=left.source,
        point_id=left.point_id or right.point_id,
        payload=left.payload or right.payload,
        snippet=left.snippet or right.snippet,
        dense_score=left.dense_score if left.dense_score is not None else right.dense_score,
        sparse_score=left.sparse_score if left.sparse_score is not None else right.sparse_score,
        rrf_score=left.rrf_score,
        rerank_score=left.rerank_score,
    )


def fuse_retrieval_results(
    dense: RetrievalResult,
    sparse: RetrievalResult,
    *,
    config: RetrievalConfig | None = None,
) -> RetrievalResult:
    """Fuse dense and sparse retrieval results for the same query."""
    policy = config or RetrievalConfig.default()
    return reciprocal_rank_fusion(
        [list(dense.candidates), list(sparse.candidates)],
        k=policy.rrf_k,
        top_k=policy.fusion_top_k,
        query=dense.query,
    )
