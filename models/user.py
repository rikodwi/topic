from beanie import Document
from pydantic import Field
from typing import Optional

class User(Document):
    id: int = Field(alias="_id")
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    role: str

    class Meta:
        collection = "users"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}"