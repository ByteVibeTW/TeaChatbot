import os
import time

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

MAX_RETRIES = 5
RETRY_INTERVAL_SECONDS = 2
VECTOR_SIZE = 768


def collection_exists(client: QdrantClient, collection_name: str) -> bool:
    try:
        client.get_collection(collection_name=collection_name)
        return True
    except UnexpectedResponse as exc:
        if exc.status_code == 404:
            return False
        raise


def init_collection(qdrant_url: str, collection_name: str) -> None:
    client = QdrantClient(url=qdrant_url)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if collection_exists(client, collection_name):
                print(f"Collection '{collection_name}' already exists. Skipping.")
                return

            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=VECTOR_SIZE,
                    distance=models.Distance.COSINE,
                ),
            )
            print(
                f"Collection '{collection_name}' created successfully with size={VECTOR_SIZE} and distance=Cosine."
            )
            return
        except UnexpectedResponse as exc:
            if exc.status_code == 409:
                print(f"Collection '{collection_name}' already exists. Skipping.")
                return
            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    f"Failed to initialize collection after {MAX_RETRIES} attempts: {exc}"
                ) from exc
            print(
                f"Attempt {attempt}/{MAX_RETRIES} failed: {exc}. Retrying in {RETRY_INTERVAL_SECONDS}s..."
            )
            time.sleep(RETRY_INTERVAL_SECONDS)
        except Exception as exc:
            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    f"Failed to initialize collection after {MAX_RETRIES} attempts: {exc}"
                ) from exc
            print(
                f"Attempt {attempt}/{MAX_RETRIES} failed: {exc}. Retrying in {RETRY_INTERVAL_SECONDS}s..."
            )
            time.sleep(RETRY_INTERVAL_SECONDS)


if __name__ == "__main__":
    load_dotenv()
    qdrant_url = os.environ.get("QDRANT_URL")
    collection_name = os.environ.get("QDRANT_COLLECTION_NAME", "knowledge")

    if not qdrant_url:
        raise ValueError("QDRANT_URL is required.")

    init_collection(qdrant_url=qdrant_url, collection_name=collection_name)
