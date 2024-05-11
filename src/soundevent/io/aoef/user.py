from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from .adapters import DataAdapter
from soundevent import data


class UserObject(BaseModel):
    """Schema definition for a user object in AOEF format."""

    uuid: UUID
    username: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    institution: Optional[str] = None


class UserAdapter(DataAdapter[data.User, UserObject, UUID, UUID]):
    def assemble_aoef(self, obj: data.User, obj_id: UUID) -> UserObject:
        return UserObject(
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
