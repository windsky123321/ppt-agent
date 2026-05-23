from pydantic import BaseModel


class PromptTemplate(BaseModel):
    id: str
    name: str
    description: str
    language: str
    content: str
    created_at: str
    updated_at: str
