import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from .adapters import DataAdapter
from .note import NoteAdapter, NoteObject
from .sequence import SequenceAdapter
from .tag import TagAdapter
from .user import UserAdapter
from soundevent import data


class SequenceAnnotationObject(BaseModel):
    """Schema definition for a sequence annotation object in AOEF format."""

    uuid: UUID
    sequence: UUID
    notes: Optional[List[NoteObject]] = None
    tags: Optional[List[int]] = None
    created_by: Optional[UUID] = None
    created_on: Optional[datetime.datetime] = None


class SequenceAnnotationAdapter(
    DataAdapter[data.SequenceAnnotation, SequenceAnnotationObject, UUID, UUID]
):
    def __init__(
        self,
        user_adapter: UserAdapter,
        tag_adapter: TagAdapter,
        note_adapter: NoteAdapter,
        sequence_adapter: SequenceAdapter,
    ):
        super().__init__()
        self.user_adapter = user_adapter
        self.tag_adapter = tag_adapter
        self.note_adapter = note_adapter
        self.sequence_adapter = sequence_adapter

    def assemble_aoef(
        self,
        obj: data.SequenceAnnotation,
        obj_id: UUID,
    ) -> SequenceAnnotationObject:
        return SequenceAnnotationObject(
            sequence=self.sequence_adapter.to_aoef(obj.sequence).uuid,
            notes=(
                [self.note_adapter.to_aoef(note) for note in obj.notes]
                if obj.notes
                else None
            ),
            tags=(
                [self.tag_adapter.to_aoef(tag).id for tag in obj.tags]
                if obj.tags
                else None
            ),
            uuid=obj.uuid,
            created_by=(
                self.user_adapter.to_aoef(obj.created_by).uuid
                if obj.created_by
                else None
            ),
            created_on=obj.created_on,
        )

    def assemble_soundevent(
        self,
        obj: SequenceAnnotationObject,
    ) -> data.SequenceAnnotation:
        sequence = self.sequence_adapter.from_id(obj.sequence)

        if sequence is None:
            raise ValueError(f"Sequence with ID {obj.sequence} not found.")

        return data.SequenceAnnotation(
            uuid=obj.uuid or uuid4(),
            sequence=sequence,
            notes=(
                [self.note_adapter.to_soundevent(note) for note in obj.notes]
                if obj.notes
                else []
            ),
            tags=[
                tag
                for tag_id in obj.tags or []
                if (tag := self.tag_adapter.from_id(tag_id)) is not None
            ],
            created_by=(
                self.user_adapter.from_id(obj.created_by)
                if obj.created_by is not None
                else None
            ),
            created_on=obj.created_on or datetime.datetime.now(),
        )
