from pydantic import BaseModel


class Knowledge(BaseModel):
    content: str
