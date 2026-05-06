from typing import Optional

from google import genai
from google.genai.types import GenerateContentConfig, ThinkingConfig


class GeminiService:
    """
    Gemini 模型服務
    """

    def __init__(
        self,
        client: genai.Client,
        model: str,
        response_type="application/json",
        model_thinking_budget=0,
    ):
        self.client = client
        self.model = model
        self.model_config = GenerateContentConfig(
            thinking_config=ThinkingConfig(thinking_budget=model_thinking_budget),
            response_mime_type=response_type,  # 強制回傳指定格式
        )
        """
        thinking_budget: int
            0: No thinking (default)
            -1: dynamic thinking (model decides the level)
            512 / 1024: Basic thinking 指定 token 數量上限
        """

    # 將問題精簡摘要
    def generate_search_query(self, question: str) -> Optional[str]:
        prompt = f"Generate a concise search query for the following question: {question}, without extra text."
        try:
            return self.client.models.generate_content(
                model="gemini-2.5-flash-lite", contents=prompt
            ).text
        except Exception as e:
            print(f"[GeminiService] Error generating search query: {e}")
            return ""  # Return empty string instead of None

    # 根據主題生成相關問題
    def generate_question(self, topic: str, response_schema=None) -> str:
        prompt = topic
        try:
            if response_schema:
                self.model_config.response_schema = response_schema
            return self.client.models.generate_content(
                model=self.model, contents=prompt, config=self.model_config
            ).text
        except Exception as e:
            print(f"[GeminiService] Error generating question: {e}")
            # Return structured error that can be caught upstream
            raise RuntimeError(f"Failed to generate question: {e}")

    # 通用的生成方法
    def generate_answer(self, prompt: str, response_schema=None) -> str:
        try:
            if response_schema:
                self.model_config.response_schema = response_schema
            return self.client.models.generate_content(
                model=self.model, contents=prompt, config=self.model_config
            ).text
        except Exception as e:
            error_msg = str(e)
            print(f"[GeminiService] Error generating answer: {error_msg}")
            # Return structured error response
            if "503" in error_msg or "high demand" in error_msg:
                raise RuntimeError(f"Gemini API is currently unavailable: {error_msg}")
            else:
                raise RuntimeError(f"Failed to generate answer: {error_msg}")
