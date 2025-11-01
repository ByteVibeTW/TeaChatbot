from application.use_cases.prompt_loader import PromptLoader
from domain.services.gemini_service import GeminiService


class GenerateQuestionsUseCase:
    """
    生成探索性問題
    """

    def __init__(self, gemini_service: GeminiService, prompt_template_file_name: str):
        self.gemini_service = gemini_service
        self.prompt_loader = PromptLoader(prompt_template_file_name)

    def execute(self, user_input: str, response_schema=None):
        topic = self.gemini_service.generate_search_query(user_input)
        prompt_template = self.prompt_loader.load_prompt()
        prompt = prompt_template.format(topic=topic)
        print(f"Final Prompt: {prompt}")
        # print(
        #     f"Generated: {self.gemini_service.generate_question(prompt, response_schema=response_schema)}"
        # )
        return self.gemini_service.generate_question(
            prompt, response_schema=response_schema
        )
