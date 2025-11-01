from typing import List

from sentence_transformers import SentenceTransformer

from infrastructure.db.vector_db import VectorDB


class InsertKnowledgeUseCase:
    """
    新增向量知識庫內容
    """

    def __init__(self, vector_db: VectorDB, embedding_model: SentenceTransformer):
        self.vector_db = vector_db
        self.embedding_model = embedding_model

    def execute(self, knowledge_list: List[str]):
        self.vector_db.insert_vectors(knowledge_list, self.embedding_model)
