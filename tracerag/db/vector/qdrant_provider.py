"""Qdrant vector storage provider."""

from __future__ import annotations

from tracerag.core.exceptions import VectorStorageError
from tracerag.db.vector.config import CollectionConfig, QdrantConfig
from tracerag.db.vector.contracts import VectorStore
from tracerag.models.vector import StoredVectorRecord, VectorSearchHit, VectorUpsertFailure, VectorUpsertResult



class QdrantVectorStore(VectorStore):
    """Vector store implementation backed by Qdrant."""

    def __init__(self, config: QdrantConfig | None = None) -> None:
        self._config = config or QdrantConfig.default()
        self._client = self._create_client()

    @property
    def collection_name(self) -> str:
        return self._config.collection.name

    @property
    def config(self) -> QdrantConfig:
        return self._config

    def _create_client(self):  # noqa: ANN202
        try:
            from qdrant_client import QdrantClient
        except ImportError as exc:
            raise VectorStorageError(
                "qdrant-client is required for QdrantVectorStore; install with: pip install qdrant-client",
                cause=exc,
            ) from exc

        return QdrantClient(
            url=self._config.url,
            api_key=self._config.api_key,
            prefer_grpc=self._config.prefer_grpc,
            timeout=self._config.timeout_seconds,
        )

    def collection_exists(self, collection_name: str | None = None) -> bool:
        name = collection_name or self.collection_name
        try:
            self._client.get_collection(name)
            return True
        except Exception:
            return False

    def bootstrap_collection(self, config: CollectionConfig | None = None) -> None:
        collection = config or self._config.collection
        if self.collection_exists(collection.name):
            if collection.recreate_if_exists:
                self._client.delete_collection(collection.name)
            else:
                return

        try:
            from qdrant_client.models import Distance, VectorParams
        except ImportError as exc:
            raise VectorStorageError("qdrant-client models import failed", cause=exc) from exc

        distance = {
            "cosine": Distance.COSINE,
            "euclid": Distance.EUCLID,
            "dot": Distance.DOT,
        }.get(collection.distance, Distance.COSINE)
        self._client.create_collection(
            collection_name=collection.name,
            vectors_config=VectorParams(size=collection.vector_size, distance=distance),
            on_disk_payload=collection.on_disk_payload,
        )

    def upsert(self, records: list[StoredVectorRecord]) -> VectorUpsertResult:
        if not records:
            return VectorUpsertResult(collection_name=self.collection_name, upserted_count=0)

        try:
            from qdrant_client.models import PointStruct
        except ImportError as exc:
            raise VectorStorageError("qdrant-client models import failed", cause=exc) from exc

        upserted = 0
        failures: list[VectorUpsertFailure] = []
        batch_size = self._config.upsert_batch_size

        for start in range(0, len(records), batch_size):
            batch = records[start : start + batch_size]
            points = [
                PointStruct(
                    id=record.point_id,
                    vector=list(record.vector),
                    payload=record.payload.model_dump(mode="json"),
                )
                for record in batch
            ]
            try:
                self._client.upsert(collection_name=self.collection_name, points=points)
                upserted += len(batch)
            except Exception as exc:
                for record in batch:
                    failures.append(
                        VectorUpsertFailure(chunk_id=record.chunk_id, error=str(exc))
                    )

        return VectorUpsertResult(
            collection_name=self.collection_name,
            upserted_count=upserted,
            failures=tuple(failures),
        )

    def search(
        self,
        query_vector: list[float],
        *,
        limit: int,
        query_filter=None,
    ) -> list[VectorSearchHit]:
        """Search the collection by vector similarity."""
        try:
            hits = self._client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=query_filter,
                with_payload=True,
            )
        except Exception as exc:
            raise VectorStorageError("Qdrant vector search failed", cause=exc) from exc

        results: list[VectorSearchHit] = []
        for hit in hits:
            payload_data = hit.payload or {}
            try:
                payload = VectorPointPayload.model_validate(payload_data)
            except Exception:
                continue
            results.append(
                VectorSearchHit(
                    point_id=str(hit.id),
                    chunk_id=payload.chunk_id,
                    score=float(hit.score),
                    payload=payload,
                )
            )
        return results
