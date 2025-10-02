from typing import List

from pydantic import BaseModel


class KnowledgeItemDTO(BaseModel):
    content: str


class KnowledgeRequestDTO(BaseModel):
    knowledge: List[KnowledgeItemDTO]


class ChapterContent(BaseModel):
    article: str
    practice: str


class CourseSection(BaseModel):
    chapter_name: str
    content: List[ChapterContent]


class CourseResponse(BaseModel):
    course_name: str
    sections: List[CourseSection]
