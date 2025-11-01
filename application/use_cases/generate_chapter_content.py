from application.dto.course_content import CourseContentRequest
from application.use_cases.prompt_loader import PromptLoader
from domain.services.gemini_service import GeminiService


class GenerateChapterContentUseCase:
    """
    生成課程章節內容
    """

    def __init__(
        self,
        gemini_service: GeminiService,
        content_prompt_template_file_name_1: str,
        practice_prompt_template_file_name_2: str,
    ):
        self.gemini_service = gemini_service
        self.content_prompt_loader = PromptLoader(content_prompt_template_file_name_1)
        self.practice_prompt_loader = PromptLoader(practice_prompt_template_file_name_2)

    def execute(self, request: CourseContentRequest, response_schema=None) -> str:
        course_name = request.course_name
        course_intro = request.intro
        section_name = request.section_name
        chapter_name = request.chapter_name
        content_prompt_template = self.content_prompt_loader.load_prompt()
        practice_prompt_template = self.practice_prompt_loader.load_prompt()
        content_prompt = content_prompt_template.format(
            courseName=course_name,
            intro=course_intro,
            sectionName=section_name,
            chapterName=chapter_name,
        )
        # practice_prompt = ""
        return self.gemini_service.generate_answer(
            content_prompt, response_schema=response_schema
        )
