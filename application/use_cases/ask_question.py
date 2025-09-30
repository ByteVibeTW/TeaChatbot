from application.use_cases.prompt_engineer import PromptEngineer
from application.use_cases.prompt_loader import PromptLoader
from domain.services.gemini_service import GeminiService
from infrastructure.db.vector_db import VectorDB
from infrastructure.external.google_search import GoogleSearch


class AskQuestionUseCase:
    def __init__(
        self,
        gemini_service: GeminiService,
        vector_db: VectorDB,
        google_search: GoogleSearch,
        prompt_template_file_name: str,
    ):
        self.gemini_service = gemini_service
        self.vector_db = vector_db
        self.google_search = google_search
        self.prompt_engineer = PromptEngineer()
        self.prompt_loader = PromptLoader(prompt_template_file_name)

    def execute(self, user_input: str) -> str:
        search_query = self.gemini_service.generate_search_query(user_input)
        google_results = self.google_search.search(search_query, max_results=10)
        vector_results = self.vector_db.query(user_input, search_limit=10)
        text1 = self.prompt_engineer.build_rag_vector_prompt(vector_results)
        text2 = self.prompt_engineer.build_rag_google_search_prompt(google_results)
        prompt_template = self.prompt_loader.load_prompt()
        prompt = prompt_template.format(text1=text1, text2=text2, userInput=user_input)
        print(f"Finial Prompt:\n{prompt}")
        return self.gemini_service.generate_answer(prompt)
