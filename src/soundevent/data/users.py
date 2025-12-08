from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class User(BaseModel):
    """Information about a user."""

    model_config = ConfigDict(from_attributes=True)

    uuid: UUID = Field(default_factory=uuid4, repr=False)

    username: str | None = Field(default=None, repr=True)

    email: EmailStr | None = Field(default=None, repr=False)

    name: str | None = Field(default=None, repr=True)

    institution: str | None = Field(default=None, repr=False)
