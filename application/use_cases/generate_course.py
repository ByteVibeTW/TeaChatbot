from application.dto.user_feedback import UserFeedbackRequest
from application.use_cases.prompt_engineer import PromptEngineer
from application.use_cases.prompt_loader import PromptLoader
from domain.services.gemini_service import GeminiService
from infrastructure.db.mysql_db import MysqlDB
from infrastructure.db.vector_db import VectorDB
from infrastructure.external.google_search import GoogleSearch


class GenerateCourseUseCase:
    def __init__(
        self,
        gemini_service: GeminiService,
        vector_db: VectorDB,
        mysql_db: MysqlDB,
        google_search: GoogleSearch,
        prompt_template_file_name: str,
    ):
        self.gemini_service = gemini_service
        self.vector_db = vector_db
        self.mysql_db = mysql_db
        self.google_search = google_search
        self.prompt_engineer = PromptEngineer()
        self.prompt_loader = PromptLoader(prompt_template_file_name)

    def execute(self, request: UserFeedbackRequest, response_schema=None) -> str:
        temp_data = self.mysql_db.fetch_user_temp(request.userId)
        if temp_data is None:
            raise ValueError(
                f"No temporary user data found for userId={request.userId}. "
                "Please call /ai/generate_questions first."
            )

        user_input = temp_data["userQuestion"]
        search_query = self.gemini_service.generate_search_query(user_input)
        google_results = self.google_search.search(search_query, max_results=10)
        vector_results = self.vector_db.query(user_input, search_limit=10)
        text1 = self.prompt_engineer.build_rag_vector_prompt(vector_results)
        text2 = self.prompt_engineer.build_rag_google_search_prompt(google_results)

        goal = ""
        for index, answer in enumerate(request.userAnswer):
            goal += f"{index + 1}. {answer.questionText} \n"
            goal += f"Answer: {answer.option} \n\n"

        prompt_template = self.prompt_loader.load_prompt()
        prompt = prompt_template.format(
            text1=text1, text2=text2, userInput=user_input, goal=goal
        )
        print(f"Final Prompt:\n{prompt}")
        # Let exceptions propagate from gemini_service
        return self.gemini_service.generate_answer(
            prompt, response_schema=response_schema
        )
