import uuid

import vecs
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


class VectorDB:
    def __init__(self, db_url: str, collection_name="AItest", dimension=768):
        self.vx = vecs.create_client(db_url)
        self.collection = self.vx.get_or_create_collection(
            name=collection_name, dimension=dimension
        )
        self.collection.create_index()

    def insert_vectors(
        self, knowledge: list[str], embedding_model: SentenceTransformer
    ):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100, chunk_overlap=20, separators=["\n", "。", "！", "？", "，"]
        )
        vectors = []
        for context in knowledge:
            chunks = text_splitter.split_text(context)
            # print(f"chunks: {chunks}")
            for chunk in chunks:
                embedding = embedding_model.encode(chunk).tolist()
                vectors.append((str(uuid.uuid4()), embedding, {"text": chunk}))
        self.collection.upsert(vectors)

    def query(self, prompt, search_limit=10) -> list:
        embedding_model = SentenceTransformer("DMetaSoul/sbert-chinese-general-v2")
        query_embedding = embedding_model.encode(prompt).tolist()
        results = self.collection.query(
            data=query_embedding,
            limit=search_limit,
            measure="cosine_distance",
            include_value=True,
            include_metadata=True,
        )
        return results
