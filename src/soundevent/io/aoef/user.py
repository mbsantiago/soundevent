from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from soundevent import data

from .adapters import DataAdapter


class UserObject(BaseModel):
    """Schema definition for a user object in AOEF format."""

    id: int
    uuid: Optional[UUID] = None
    username: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    institution: Optional[str] = None


class UserAdapter(DataAdapter[data.User, UserObject]):
    def assemble_aoef(self, obj: data.User, obj_id: int) -> UserObject:
        return UserObject(
            id=obj_id,
            uuid=obj.uuid,
            username=obj.username,
            email=obj.email,
            name=obj.name,
            institution=obj.institution,
        )

    def assemble_soundevent(self, obj: UserObject) -> data.User:
        return data.User(
            uuid=obj.uuid or uuid4(),
            username=obj.username,
            email=obj.email,
            name=obj.name,
            institution=obj.institution,
        )
