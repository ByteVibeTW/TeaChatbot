from typing import List

from pydantic import BaseModel


class QuestionSection(BaseModel):
    question_text: str
    options: List[str]


class UserQuestionResponse(BaseModel):
    questions: List[QuestionSection]
