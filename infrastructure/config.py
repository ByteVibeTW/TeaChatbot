import os

import google.generativeai as genai
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


class Config:
    def __init__(self):
        load_dotenv()
        self.GEMINI_API_KEY = os.environ.get("GOOGLE_GEMINI_API_KEY")
        self.SEARCH_API_KEY = os.environ.get("GOOGLE_SEARCH_API_KEY")
        self.SEARCH_ENGINE_ID = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
        self.DB_URL = os.environ.get("DB_URL")
        self.GEMINI_MODEL = os.environ.get("GEMINI_MODEL")
        self.EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL")

    def configure_gemini(self) -> genai.GenerativeModel:
        genai.configure(api_key=self.GEMINI_API_KEY)
        return genai.GenerativeModel(self.GEMINI_MODEL)

    def get_embedding_model(self):
        return SentenceTransformer("DMetaSoul/sbert-chinese-general-v2")
