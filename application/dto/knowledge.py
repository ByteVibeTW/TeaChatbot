from typing import List

from pydantic import BaseModel


class KnowledgeItem(BaseModel):
    content: str


class KnowledgeRequest(BaseModel):
    knowledge: List[KnowledgeItem]
