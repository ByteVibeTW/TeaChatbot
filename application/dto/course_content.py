from pydantic import BaseModel


class CourseContentRequest(BaseModel):
    courseName: str
    intro: str
    sectionName: str
    chapterId: int
    chapterName: str


class CourseContentResponse(BaseModel):
    content: str
