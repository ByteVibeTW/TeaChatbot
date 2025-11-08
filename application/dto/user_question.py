from typing import List

from pydantic import BaseModel


class QuestionSection(BaseModel):
    questionText: str
    options: List[str]


class UserQuestionResponse(BaseModel):
    questions: List[QuestionSection]
