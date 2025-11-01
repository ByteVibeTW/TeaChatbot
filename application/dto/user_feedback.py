from typing import List

from pydantic import BaseModel


class UserAnswerSection(BaseModel):
    question_text: str
    option: str


class UserFeedbackRequest(BaseModel):
    user_id: int
    user_answer: List[UserAnswerSection]
