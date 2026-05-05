import os

from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer


class Config:
    def __init__(self):
        load_dotenv()
        self.GEMINI_API_KEY = os.environ.get("GOOGLE_GEMINI_API_KEY")
        self.SEARCH_API_KEY = os.environ.get("GOOGLE_SEARCH_API_KEY")
        self.SEARCH_ENGINE_ID = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
        self.QDRANT_URL = os.environ.get("QDRANT_URL")
        self.QDRANT_COLLECTION_NAME = os.environ.get(
            "QDRANT_COLLECTION_NAME", "knowledge"
        )
        self.MYSQL_HOST = os.environ.get("MYSQL_HOST")
        self.MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
        self.MYSQL_USER = os.environ.get("MYSQL_USER")
        self.MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
        self.MYSQL_DB = os.environ.get("MYSQL_DB")
        self.GEMINI_MODEL = os.environ.get("GEMINI_MODEL")
        self.EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL")
        self.THINKING_BUDGET = int(os.environ.get("THINKING_BUDGET", "-1"))
        self.WEB_API_URL = os.environ.get("WEB_API_URL")

    def configure_gemini(self) -> genai.Client:
        return genai.Client(api_key=self.GEMINI_API_KEY)

    def get_embedding_model(self):
        return SentenceTransformer(self.EMBEDDING_MODEL)
