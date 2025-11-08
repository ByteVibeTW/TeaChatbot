from typing import List

from pydantic import BaseModel


class UserAnswerSection(BaseModel):
    questionText: str
    option: str


class UserFeedbackRequest(BaseModel):
    userId: str
    userAnswer: List[UserAnswerSection]
