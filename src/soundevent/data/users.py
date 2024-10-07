from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class User(BaseModel):
    """Information about a user."""

    model_config = ConfigDict(from_attributes=True)

    uuid: UUID = Field(default_factory=uuid4, repr=False)

    username: Optional[str] = Field(None, repr=True)

    email: Optional[EmailStr] = Field(None, repr=False)

    name: Optional[str] = Field(None, repr=True)

    institution: Optional[str] = Field(None, repr=False)
