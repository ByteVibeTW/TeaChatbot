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
        self.SUPABASE_URL = os.environ.get("SUPABASE_URL")
        self.SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
        self.DB_URL = os.environ.get("DB_URL")
        self.GEMINI_MODEL = os.environ.get("GEMINI_MODEL")
        self.EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL")
        self.THINKING_BUDGET = os.environ.get("THINKING_BUDGET")
        self.WEB_API_URL = os.environ.get("WEB_API_URL")

    def configure_gemini(self) -> genai.Client:
        return genai.Client(api_key=self.GEMINI_API_KEY)

    def get_embedding_model(self):
        return SentenceTransformer("DMetaSoul/sbert-chinese-general-v2")
