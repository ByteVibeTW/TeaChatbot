from typing import List

from pydantic import BaseModel


class ChapterContent(BaseModel):
    article: str
    practice: str


class CourseSection(BaseModel):
    chapter_name: str
    content: List[ChapterContent]


class CourseResponse(BaseModel):
    course_name: str
    sections: List[CourseSection]
