from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """Information about a user."""

    uuid: UUID = Field(default_factory=uuid4)
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    institution: Optional[str] = None
