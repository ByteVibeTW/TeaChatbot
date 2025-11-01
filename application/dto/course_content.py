from pydantic import BaseModel


class CourseContentRequest(BaseModel):
    course_name: str
    intro: str
    section_name: str
    chapter_id: int
    chapter_name: str


class CourseContentResponse(BaseModel):
    content: str
