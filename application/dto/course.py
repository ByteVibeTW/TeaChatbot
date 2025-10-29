from typing import List

from pydantic import BaseModel


class CourseSection(BaseModel):
    chapter_name: str
    description: str
    content: List[str]


class CourseResponse(BaseModel):
    course_name: str
    intro: str
    sections: List[CourseSection]
