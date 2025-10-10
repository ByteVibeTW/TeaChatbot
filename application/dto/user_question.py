from typing import List

from pydantic import BaseModel


class QuestionSection(BaseModel):
    question_text: str
    options: List[str]


class UserQuestionRequest(BaseModel):
    questions: List[QuestionSection]
