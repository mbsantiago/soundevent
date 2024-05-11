import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from .adapters import DataAdapter
from .note import NoteObject
from soundevent import data


class SoundEventAnnotationObject(BaseModel):
    """Schema definition for an annotation object in AOEF format."""

    uuid: UUID
    sound_event: UUID
    notes: Optional[List[NoteObject]] = None
    tags: Optional[List[int]] = None
    created_by: Optional[UUID] = None
    created_on: Optional[datetime.datetime] = None


class SoundEventAnnotationAdapter(
    DataAdapter[
        data.SoundEventAnnotation, SoundEventAnnotationObject, UUID, UUID
    ]
):
    def __init__(
        self,
        user_adapter,
        tag_adapter,
        note_adapter,
        sound_event_adapter,
    ):
        super().__init__()
        self.user_adapter = user_adapter
        self.tag_adapter = tag_adapter
        self.note_adapter = note_adapter
        self.sound_event_adapter = sound_event_adapter

    def assemble_aoef(
        self,
        obj: data.SoundEventAnnotation,
        obj_id: UUID,
    ) -> SoundEventAnnotationObject:
        return SoundEventAnnotationObject(
            sound_event=self.sound_event_adapter.to_aoef(obj.sound_event).uuid,
            notes=(
                [self.note_adapter.to_aoef(note) for note in obj.notes]
                if obj.notes
                else None
            ),
            tags=[self.tag_adapter.to_aoef(tag).id for tag in obj.tags],
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
        obj: SoundEventAnnotationObject,
    ) -> data.SoundEventAnnotation:
        sound_event = self.sound_event_adapter.from_id(obj.sound_event)

        if sound_event is None:
            raise ValueError(
                f"Sound event with ID {obj.sound_event} not found."
            )

        return data.SoundEventAnnotation(
            uuid=obj.uuid,
            sound_event=sound_event,
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
