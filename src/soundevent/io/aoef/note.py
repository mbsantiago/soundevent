import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from .user import UserAdapter
from soundevent import data


class NoteObject(BaseModel):
    """Schema definition for a note object in AOEF format."""

    uuid: UUID
    message: str
    created_by: Optional[UUID] = None
    is_issue: bool = False
    created_on: Optional[datetime.datetime] = None


class NoteAdapter:
    def __init__(self, user_adapter: UserAdapter):
        self._user_adapter = user_adapter

    def to_aoef(self, note: data.Note) -> NoteObject:
        user_id = None
        if note.created_by is not None:
            user_id = self._user_adapter.to_aoef(note.created_by).uuid

        return NoteObject(
            uuid=note.uuid,
            message=note.message,
            created_by=user_id,
            is_issue=note.is_issue,
            created_on=note.created_on,
        )

    def to_soundevent(self, note: NoteObject) -> data.Note:
        user = None
        if note.created_by is not None:
            user = self._user_adapter.from_id(note.created_by)

        return data.Note(
            uuid=note.uuid or uuid4(),
            message=note.message,
            created_by=user,
            is_issue=note.is_issue,
            created_on=note.created_on or datetime.datetime.now(),
        )
