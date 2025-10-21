from typing import List

from pydantic import BaseModel


class CourseSection(BaseModel):
    chapter_name: str
    content: List[str]


class CourseResponse(BaseModel):
    course_name: str
    sections: List[CourseSection]
