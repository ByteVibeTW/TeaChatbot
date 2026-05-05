import uuid
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse
from sentence_transformers import SentenceTransformer


class VectorDB:
    def __init__(self, qdrant_url: str, collection_name: str = "knowledge"):
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.client = QdrantClient(url=qdrant_url)
        self._validate_collection_exists()

    def _validate_collection_exists(self) -> None:
        try:
            self.client.get_collection(self.collection_name)
        except UnexpectedResponse as exc:
            if exc.status_code == 404:
                raise ValueError(
                    f"Qdrant collection '{self.collection_name}' does not exist. "
                    "Please run `python init_qdrant.py` first."
                ) from exc
            raise
        except Exception as exc:
            raise ConnectionError(
                f"Unable to connect to Qdrant at '{self.qdrant_url}': {exc}"
            ) from exc

    def insert_vectors(
        self, knowledge: list[str], embedding_model: SentenceTransformer
    ) -> None:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=20,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " "],
        )

        points: list[models.PointStruct] = []
        for context in knowledge:
            chunks = text_splitter.split_text(context)
            for chunk in chunks:
                embedding = embedding_model.encode(chunk).tolist()
                points.append(
                    models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={"text": chunk},
                    )
                )

        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)

    def query(
        self, prompt: str, search_limit: int = 10
    ) -> list[tuple[str, float, dict[str, Any]]]:
        embedding_model = SentenceTransformer("DMetaSoul/sbert-chinese-general-v2")
        query_embedding = embedding_model.encode(prompt).tolist()

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=search_limit,
            with_payload=True,
        )

        results: list[tuple[str, float, dict[str, Any]]] = []
        for point in response.points:
            payload = point.payload or {}
            metadata = {"text": str(payload.get("text", ""))}
            # Keep vecs-compatible distance semantics: smaller means more similar.
            distance = 1 - point.score
            results.append((str(point.id), distance, metadata))

        return results
