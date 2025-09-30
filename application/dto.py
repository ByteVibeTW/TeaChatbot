from typing import List

from pydantic import BaseModel


class KnowledgeItemDTO(BaseModel):
    content: str


class KnowledgeRequestDTO(BaseModel):
    knowledge: List[KnowledgeItemDTO]


class AnswerResponseDTO(BaseModel):
    answer: str
