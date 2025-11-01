import json

from fastapi import FastAPI

from application.dto.course import CourseResponse
from application.dto.course_content import CourseContentRequest, CourseContentResponse
from application.dto.knowledge import KnowledgeRequest
from application.dto.user_feedback import UserFeedbackRequest
from application.dto.user_question import UserQuestionRequest
from application.use_cases.create_user_temp import CreateUserTempUseCase
from application.use_cases.generate_chapter_content import GenerateChapterContentUseCase
from application.use_cases.generate_course import GenerateCourseUseCase
from application.use_cases.generate_questions import GenerateQuestionsUseCase
from application.use_cases.insert_knowledge import InsertKnowledgeUseCase
from domain.services.api_request_service import APIRequest
from domain.services.gemini_service import GeminiService
from infrastructure.config import Config
from infrastructure.db.vector_db import VectorDB
from infrastructure.external.google_search import GoogleSearch

tags_metadata = [
    {"name": "知識庫模組", "description": "RAG 知識庫相關 API"},
    {"name": "生成課程模組", "description": "調用大語言模型生成課程與內容"},
]


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI 助教課程生成 API",
        description="此 API 提供 AI 助教課程生成相關功能，包括知識庫管理、問題生成及課程大綱等。",
        version="1.0.0",
        openapi_tags=tags_metadata,
    )

    # variables
    temp_file_name = "user_temp.json"  # 使用者暫存檔案名稱

    # Initialize configuration and services
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
    api_request_service = APIRequest(api_url=config.WEB_API_URL)

    # Initialize use cases
    insert_knowledge_use_case = InsertKnowledgeUseCase(vector_db, embedding_model)
    generate_questions_use_case = GenerateQuestionsUseCase(
        gemini_service, prompt_template_file_name="exploratory_question.txt"
    )
    create_user_temp_use_case = CreateUserTempUseCase(temp_file_name)
    generate_course_use_case = GenerateCourseUseCase(
        gemini_service,
        vector_db,
        google_search,
        prompt_template_file_name="course_prompt_template.txt",
        temp_file_name=temp_file_name,
    )
    generate_chapter_content_use_case = GenerateChapterContentUseCase(
        gemini_service,
        content_prompt_template_file_name_1="chapter_content_template.txt",
        practice_prompt_template_file_name_2="chapter_practice_template.txt",
    )

    # Define API endpoints
    @app.get("/health", summary="Health Check", tags=["health-controller"])
    def health_check():
        return {"status": "ok"}

    @app.post(
        "/rag/insert_knowledge",
        summary="新增知識到向量資料庫",
        tags=["知識庫模組"],
    )
    def insert_knowledge(request: KnowledgeRequest):
        insert_knowledge_use_case.execute([item.content for item in request.knowledge])
        return {"message": "Knowledge inserted successfully."}

    @app.get(
        "/ai/generate_questions/{userId}/{userInput}",
        summary="生成額外問題",
        tags=["生成課程模組"],
        response_model=UserQuestionRequest,
    )
    def generate_questions(userId: str, userInput: str):
        questions = json.loads(
            generate_questions_use_case.execute(
                userInput, response_schema=UserQuestionRequest
            )
        )
        create_user_temp_use_case.execute(userId, userInput, questions)
        return questions

    @app.post("/ai/generate_course", summary="生成課程與大綱", tags=["生成課程模組"])
    def generate_course(request: UserFeedbackRequest):
        course = json.loads(
            generate_course_use_case.execute(request, response_schema=CourseResponse)
        )
        create_course_payload = {
            "name": course["course_name"],
            "type": "AI 助教生成課程",
            "intro": course["intro"],
            "outline": "",
            "sections": [],
        }
        for section_index, section in enumerate(course["sections"]):
            section_template = {
                "sectionName": section["chapter_name"],
                "description": section["description"],
                "orderIndex": section_index + 1,
                "chapters": [],
            }
            for chapter_index, chapter in enumerate(section["content"]):
                chapter_template = {
                    "chapterName": chapter,
                    "content": "",
                    "orderIndex": chapter_index + 1,
                }
                section_template["chapters"].append(chapter_template)
            create_course_payload["sections"].append(section_template)
            create_course_payload["outline"] += f"{section_template['sectionName']}\n"
        print(create_course_payload)
        api_request_service.execute(
            "POST", endpoint="courses/detail", payload=create_course_payload
        )
        return course

    @app.post(
        "/ai/generate_chapter_content",
        summary="生成課程章節內容",
        tags=["生成課程模組"],
    )
    def generate_chapter_content(request: CourseContentRequest):
        chapter_content = json.loads(
            generate_chapter_content_use_case.execute(
                request, response_schema=CourseContentResponse
            )
        )
        api_request_service.execute(
            "PUT", endpoint=f"chapters/{request.chapter_id}", payload=chapter_content
        )
        return {"message": "Chapter content generated successfully."}

    return app
