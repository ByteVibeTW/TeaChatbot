import json

from fastapi import FastAPI

from application.dto.course import CourseResponse
from application.dto.course_content import CourseContentRequest, CourseContentResponse
from application.dto.knowledge import KnowledgeRequest
from application.dto.user_feedback import UserFeedbackRequest
from application.dto.user_question import UserQuestionResponse
from application.use_cases.create_user_temp import CreateUserTempUseCase
from application.use_cases.generate_chapter_content import GenerateChapterContentUseCase
from application.use_cases.generate_course import GenerateCourseUseCase
from application.use_cases.generate_questions import GenerateQuestionsUseCase
from application.use_cases.insert_knowledge import InsertKnowledgeUseCase
from domain.services.api_request_service import APIRequest
from domain.services.gemini_service import GeminiService
from init_qdrant import init_collection
from infrastructure.config import Config
from infrastructure.db.mysql_db import MysqlDB
from infrastructure.db.vector_db import VectorDB
from infrastructure.external.google_search import GoogleSearch


def _create_vector_db_with_auto_init(config: Config, mysql_db: MysqlDB) -> VectorDB:
    task_name = f"qdrant-init:{config.QDRANT_COLLECTION_NAME}"

    if not mysql_db.is_init_completed(task_name):
        print(f"[Startup] Qdrant init record not found for '{task_name}', initializing.")
        init_collection(config.QDRANT_URL, config.QDRANT_COLLECTION_NAME)
        mysql_db.mark_init_completed(
            task_name=task_name,
            details={"collection": config.QDRANT_COLLECTION_NAME},
        )
        print(f"[Startup] Qdrant init completed and recorded: {task_name}")
    else:
        print(f"[Startup] Qdrant init already recorded, skip init: {task_name}")

    try:
        return VectorDB(
            qdrant_url=config.QDRANT_URL,
            collection_name=config.QDRANT_COLLECTION_NAME,
        )
    except ValueError as exc:
        if "does not exist" not in str(exc):
            raise

        print(
            "[Startup] Qdrant init record exists but collection is missing. Reinitializing now."
        )
        init_collection(config.QDRANT_URL, config.QDRANT_COLLECTION_NAME)
        mysql_db.mark_init_completed(
            task_name=task_name,
            details={
                "collection": config.QDRANT_COLLECTION_NAME,
                "reinitialized": True,
            },
        )
        return VectorDB(
            qdrant_url=config.QDRANT_URL,
            collection_name=config.QDRANT_COLLECTION_NAME,
        )


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI 助教課程生成 API",
        description="此 API 提供 AI 助教課程生成相關功能，包括知識庫管理、問題生成及課程大綱等。",
        version="1.0.0",
    )

    config = Config()
    gemini_client = config.configure_gemini()
    embedding_model = config.get_embedding_model()
    mysql_db = MysqlDB(
        host=config.MYSQL_HOST,
        port=config.MYSQL_PORT,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DB,
    )
    vector_db = _create_vector_db_with_auto_init(config, mysql_db)
    gemini_service = GeminiService(
        gemini_client,
        config.GEMINI_MODEL,
        model_thinking_budget=config.THINKING_BUDGET,
    )
    google_search = GoogleSearch(config.SEARCH_API_KEY, config.SEARCH_ENGINE_ID)
    api_request_service = APIRequest(
        api_url=config.WEB_API_URL,
        auth_token=config.WEB_API_TOKEN,
        username=config.WEB_API_USERNAME,
        password=config.WEB_API_PASSWORD,
    )

    insert_knowledge_use_case = InsertKnowledgeUseCase(vector_db, embedding_model)
    generate_questions_use_case = GenerateQuestionsUseCase(
        gemini_service, prompt_template_file_name="exploratory_question.txt"
    )
    create_user_temp_use_case = CreateUserTempUseCase(mysql_db)
    generate_course_use_case = GenerateCourseUseCase(
        gemini_service,
        vector_db,
        mysql_db,
        google_search,
        prompt_template_file_name="course_prompt_template.txt",
    )
    generate_chapter_content_use_case = GenerateChapterContentUseCase(
        gemini_service,
        content_prompt_template_file_name_1="chapter_content_template.txt",
        practice_prompt_template_file_name_2="chapter_practice_template.txt",
    )

    @app.get("/health", summary="Health Check", tags=["health-controller"])
    def health_check():
        return {"status": "ok"}

    @app.post("/rag/insert_knowledge", summary="Insert knowledge", tags=["rag"])
    def insert_knowledge(request: KnowledgeRequest):
        insert_knowledge_use_case.execute([item.content for item in request.knowledge])
        return {"message": "Knowledge inserted successfully."}

    @app.get(
        "/ai/generate_questions/{userId}/{userInput}",
        summary="Generate exploratory questions",
        tags=["ai-course"],
        response_model=UserQuestionResponse,
    )
    def generate_questions(userId: str, userInput: str):
        questions = json.loads(
            generate_questions_use_case.execute(
                userInput, response_schema=UserQuestionResponse
            )
        )
        create_user_temp_use_case.execute(userId, userInput, questions)
        return questions

    @app.post("/ai/generate_course", summary="Generate course", tags=["ai-course"])
    def generate_course(request: UserFeedbackRequest):
        try:
            response_text = generate_course_use_case.execute(request, response_schema=CourseResponse)
            course = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse course response as JSON: {e}")
        except RuntimeError as e:
            raise ValueError(f"AI service error: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error during course generation: {e}")
        
        # Build outline from sections
        outline = ""
        for section in course["sections"]:
            outline += f"{section['chapterName']}\n"
        
        # Step 1: Create course
        create_course_payload = {
            "name": course["courseName"],
            "type": "AI Generated Course",
            "intro": course["intro"],
            "outline": outline,
        }
        print("Creating course with payload: ", create_course_payload)
        created_course = api_request_service.execute(
            "POST", endpoint="api/v1/courses", payload=create_course_payload
        )
        course_id = created_course["id"]
        print(f"Course created with ID: {course_id}")

        # Step 2: Create sections and chapters
        for section_index, section in enumerate(course["sections"]):
            # Create section
            create_section_payload = {
                "courseId": course_id,
                "sectionName": section["chapterName"],
                "orderIndex": section_index + 1,
            }
            print(f"Creating section with payload: {create_section_payload}")
            created_section = api_request_service.execute(
                "POST", endpoint="api/v1/sections", payload=create_section_payload
            )
            section_id = created_section["id"]
            print(f"Section created with ID: {section_id}")

            # Create chapters within the section
            for chapter_index, chapter in enumerate(section["content"]):
                create_chapter_payload = {
                    "sectionId": section_id,
                    "chapterName": chapter,
                    "content": "",
                    "orderIndex": chapter_index + 1,
                }
                print(f"Creating chapter with payload: {create_chapter_payload}")
                created_chapter = api_request_service.execute(
                    "POST", endpoint="api/v1/chapters", payload=create_chapter_payload
                )
                print(f"Chapter created with ID: {created_chapter['id']}")

        # Step 3: Enroll user in the course
        try:
            # Convert userId to Long/int for API
            student_id = int(request.userId) if isinstance(request.userId, str) else request.userId
            api_request_service.execute(
                "POST",
                endpoint="api/v1/enrollments",
                payload={"studentId": student_id, "courseId": course_id},
            )
        except Exception as e:
            print(f"[Warning] Failed to enroll user {request.userId} in course {course_id}: {e}")
            # Don't fail the entire operation if enrollment fails
        
        return {
            "status": "Course created successfully.",
            "courseId": course_id,
        }

    @app.post(
        "/ai/generate_chapter_content",
        summary="Generate chapter content",
        tags=["ai-course"],
    )
    def generate_chapter_content(request: CourseContentRequest):
        try:
            chapter_content = generate_chapter_content_use_case.execute(
                request, response_schema=CourseContentResponse
            )
            print({"content": chapter_content})
            api_request_service.execute(
                "PUT",
                endpoint=f"api/v1/chapters/{request.chapterId}",
                payload={"content": chapter_content},
            )
            return {"status": "Chapter content updated successfully."}
        except Exception as e:
            print(f"[Error] Failed to generate/update chapter content: {e}")
            raise

    return app
