from typing import List


class PromptEngineer:
    """
    提示詞工程與上下文整理
    """

    def __init__(self):
        pass

    def build_rag_vector_prompt(
        self, results: List[tuple], threshold: float = 0.35
    ) -> str:
        """
        將向量資料庫檢索結果整理成 prompt

        Args:
            results: list of tuples -> (id, score, metadata)
        """
        context_text = ""
        for result in results:
            # result[2] 是 metadata dict
            if result[1] < threshold:
                context_text += f"{result[2]['text']}\n"
        if not context_text:
            context_text = "無相關知識"
        return context_text

    def build_rag_google_search_prompt(self, results: List[dict]) -> str:
        """
        將 Google 搜尋結果整理成 prompt
        Args:
            results: list of dict -> {'title':..., 'snippet':...}
        """
        prompt = ""
        for result in results:
            prompt += f"Title: {result['title']}\nSnippet: {result['snippet']}\n\n"
        return prompt
