from typing import List, Optional
from beanie import Document
from pydantic import BaseModel, Field

class Topic(BaseModel):
    id: int
    title: str
    allow: Optional[List[int]] = Field(default_factory=list)

class Grup(Document):
    id: int = Field(alias="_id")
    chat_id: int
    title: str
    from_id: int
    topics: Optional[List[Topic]] = Field(default_factory=list)  # Menyimpan array data topik

    class Meta:
        collection = "group"
