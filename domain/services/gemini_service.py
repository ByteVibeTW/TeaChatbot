from typing import Optional

import google.generativeai as gemini


class GeminiService:
    def __init__(self, model: gemini.GenerativeModel):
        self.model = model

    def generate_search_query(self, question: str) -> Optional[str]:
        prompt = f"Generate a concise search query for the following question: {question}, without extra text."
        try:
            return self.model.generate_content(prompt).text
        except Exception as e:
            print(f"[GeminiService] Error generating search query: {e}")
            return None

    def generate_answer(self, prompt: str) -> str:
        try:
            return self.model.generate_content(prompt).text
        except Exception as e:
            print(f"[GeminiService] Error generating answer: {e}")
            return "抱歉，發生錯誤，無法生成回答。"
