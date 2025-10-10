import json

from fastapi import FastAPI

from application.dto.course import CourseResponse
from application.dto.knowledge import KnowledgeRequest
from application.dto.user_question import UserQuestionRequest
from application.use_cases.ask_question import AskQuestionUseCase
from application.use_cases.generate_questions import GenerateQuestionsUseCase
from application.use_cases.insert_knowledge import InsertKnowledgeUseCase
from domain.services.gemini_service import GeminiService
from infrastructure.config import Config
from infrastructure.db.vector_db import VectorDB
from infrastructure.external.google_search import GoogleSearch


def create_app() -> FastAPI:
    app = FastAPI()

    # Initialize configuration, models, and database
    config = Config()
    gemini_client = config.configure_gemini()
    embedding_model = config.get_embedding_model()
    vector_db = VectorDB(config.DB_URL)
    gemini_service = GeminiService(
        gemini_client,
        config.GEMINI_MODEL,
        model_thinking_budget=config.THINKING_BUDGET,
    )
    google_search = GoogleSearch(config.SEARCH_API_KEY, config.SEARCH_ENGINE_ID)

    # Initialize use cases
    insert_knowledge_use_case = InsertKnowledgeUseCase(vector_db, embedding_model)
    generate_questions_use_case = GenerateQuestionsUseCase(
        gemini_service, prompt_template_file_name="exploratory_question.txt"
    )
    ask_question_use_case = AskQuestionUseCase(
        gemini_service,
        vector_db,
        google_search,
        prompt_template_file_name="course_prompt_template.txt",
    )

    # Define API endpoints
    @app.get("/health/")
    def health_check():
        return {"status": "ok"}

    @app.post("/insert_knowledge/")
    def insert_knowledge(request: KnowledgeRequest):
        insert_knowledge_use_case.execute([item.content for item in request.knowledge])
        return {"message": "Knowledge inserted successfully."}

    @app.get("/generate_questions/", response_model=UserQuestionRequest)
    def generate_questions(userInput: str):
        questions = json.loads(
            generate_questions_use_case.execute(
                userInput, response_schema=UserQuestionRequest
            )
        )
        return questions

    # def user_feedback(request: UserFeedbackRequest):
    #     pass

    @app.get("/ask/", response_model=CourseResponse)
    def ask_question(userInput: str):
        answer = json.loads(
            ask_question_use_case.execute(userInput, response_schema=CourseResponse)
        )
        return answer

    return app
