from typing import List

from pydantic import BaseModel


class CourseSection(BaseModel):
    chapterName: str
    description: str
    content: List[str]


class CourseResponse(BaseModel):
    courseName: str
    intro: str
    sections: List[CourseSection]
