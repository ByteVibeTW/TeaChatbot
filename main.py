import os
from typing import List

import google.generativeai as genai
import requests
import uvicorn
import vecs
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer


class KnowledgeItem(BaseModel):
    content: str


class KnowledgeRequest(BaseModel):
    knowledge: List[KnowledgeItem]


class AnswerResponse(BaseModel):
    answer: str


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
        """
        # embedding model list
        DMetaSoul/sbert-chinese-general-v2: 基於中文BERT，專門針對中文語義相似度和檢索優化。
        all-mpnet-base-v2: 效果較佳的多語言句子編碼器。
        all-MiniLM-L6-v2: 輕量且速度快的多語言句子編碼器。
        """


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
        index = 1
        for context in knowledge:
            chunks = text_splitter.split_text(context)
            print(f"chunks: {chunks}")
            for chunk in chunks:
                embedding = embedding_model.encode(chunk).tolist()
                vectors.append((index, embedding, {"text": chunk}))
                index += 1
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


class GeminiService:
    def __init__(self, model: genai.GenerativeModel):
        self.model = model

    def generate_search_query(self, question: str) -> str:
        prompt = f"Generate a concise search query for the following question: {question}, without any additional text and markdown type."
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating search query: {e}")
            return None

    def generate_answer(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating answer: {e}")
            return "抱歉，發生錯誤，無法生成回答。"


class GoogleSearch:
    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id

    def search(self, query: str, max_results=5) -> list:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": self.api_key, "cx": self.search_engine_id, "q": query}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            results = response.json().get("items", [])
            formattedResults = []
            for item in results[:max_results]:
                formattedResults.append(
                    {"title": item.get("title", ""), "snippet": item.get("snippet", "")}
                )
            return formattedResults

        except Exception as e:
            print(f"Error during Google Search: {e}")
            return []


class PromptEngineer:
    def __init__(self):
        pass

    def build_rag_vector_prompt(self, results, threshold: float = 0.35) -> str:
        contextText = ""
        for result in results:
            print(f"ID: {result[0]}, Score: {result[1]}, Text: {result[2]['text']}")
            if result[1] < threshold:
                contexts = result[2]["text"]
                contextText += f"{contexts}\n"
        if contextText == "":
            contextText = "無相關知識"
        return contextText

    def build_rag_google_search_prompt(self, results) -> str:
        prompt = ""
        for result in results:
            prompt += f"Title: {result['title']}\nSnippet: {result['snippet']}\n\n"
        return prompt


def main():
    app = FastAPI()
    config = Config()
    model = config.configure_gemini()
    embeddingModel = config.get_embedding_model()
    vectorDB = VectorDB(config.DB_URL)
    knowledge = [
        "AIoT 是人工智慧與物聯網的結合，AI 是人工智慧的縮寫，物聯網是 Internet of Things 的縮寫。",
        "Clean Architecture 是一種軟體設計方法。",
        "DevOps 是開發與運維的結合。",
        "Kubernetes 是一個開源的容器編排平台。",
        "Microservices 是一種軟體架構風格。",
        "Docker 是一個開源的容器化平台。",
        "HTTPS 是一種安全的超文本傳輸協議。",
        "HTTP 是超文本傳輸協議的縮寫。",
        "API 是應用程式介面的縮寫。",
        "網路安全是保護網路和資料免受攻擊、損壞或未經授權訪問的實踐。",
        "雲端運算是通過互聯網提供計算服務的實踐。",
    ]

    @app.post("/insert/")
    def insert_knowledge(request: KnowledgeRequest):
        vectorDB.insert_vectors(
            [item.content for item in request.knowledge], embedding_model=embeddingModel
        )

    @app.get("/ask/", response_model=AnswerResponse)
    def run(userInput: str):
        gemini = GeminiService(model)
        searchQuery = gemini.generate_search_query(userInput)
        googleSearch = GoogleSearch(config.SEARCH_API_KEY, config.SEARCH_ENGINE_ID)
        googleSearchResults = googleSearch.search(searchQuery, max_results=10)
        vectorSearchResults = vectorDB.query(userInput, search_limit=10)
        promptEngineer = PromptEngineer()
        text1 = promptEngineer.build_rag_vector_prompt(
            vectorSearchResults, threshold=0.35
        )
        text2 = promptEngineer.build_rag_google_search_prompt(googleSearchResults)
        prompt = f"""
你是一位授課老師，搭配相關知識的內容回答問題，讓學生能夠學習路徑。

# 相關知識：
{text1}

# 外部相關知識：
{text2}

# 問題：
{userInput}

# 輸出內容規格：
依照以下大綱整理內容:
- 課程標題
- 課程章節
- 課程內容與測驗題目

# 注意事項：
- 內容越詳細越好。
- 請務必依照輸出內容規格進行回答。
- 請務必使用 json 格式進行回答。
- 請勿生成 json 以外的格式內容。

# 範例輸出：
{{
  "課程標題": "AIoT 應用介紹",
  "課程章節": [
    "第一章: AIoT 概述",
    "第二章: AIoT 技術",
    "第三章: AIoT 應用案例"
  ],
  "課程內容": {{
    "第一章: AIoT 概述": "AIoT 是人工智慧與物聯網的結合，AI 是人工智慧的縮寫，物聯網是 Internet of Things 的縮寫。",
    "第二章: AIoT 技術": "AIoT 結合了人工智慧和物聯網技術，包括感測器、資料分析、機器學習等。",
    "第三章: AIoT 應用案例": "AIoT 在智慧家庭、智慧城市、工業自動化等領域有廣泛應用。"
  }}
}}
"""
        response = gemini.generate_answer(prompt)
        print(f"Finial Prompt:\n{prompt}\n===============================\n")
        print("Answer:", response)
        return {"answer": response}

    uvicorn.run(app, host="0.0.0.0", port=8081)


if __name__ == "__main__":
    main()
