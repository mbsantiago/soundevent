from typing import List, Optional
from uuid import UUID, uuid4

import datetime
from pydantic import BaseModel

from soundevent import data

from .adapters import DataAdapter
from .clip import ClipAdapter
from .note import NoteAdapter, NoteObject
from .sound_event_annotation import SoundEventAnnotationAdapter
from .tag import TagAdapter


class ClipAnnotationsObject(BaseModel):
    """Schema definition for the clip annotations object in AOEF format."""

    id: int
    uuid: Optional[UUID] = None
    clip: int
    tags: Optional[List[int]] = None
    annotations: Optional[List[int]] = None
    notes: Optional[List[NoteObject]] = None
    created_on: Optional[datetime.datetime] = None


class ClipAnnotationsAdapter(
    DataAdapter[data.ClipAnnotations, ClipAnnotationsObject]
):
    def __init__(
        self,
        clip_adapter: ClipAdapter,
        tag_adapter: TagAdapter,
        note_adapter: NoteAdapter,
        sound_event_annotation_adapter: SoundEventAnnotationAdapter,
    ):
        super().__init__()
        self.clip_adapter = clip_adapter
        self.tag_adapter = tag_adapter
        self.note_adapter = note_adapter
        self.sound_event_annotation_adapter = sound_event_annotation_adapter

    def assemble_aoef(
        self,
        obj: data.ClipAnnotations,
        obj_id: int,
    ) -> ClipAnnotationsObject:
        return ClipAnnotationsObject(
            id=obj_id,
            uuid=obj.uuid,
            clip=self.clip_adapter.to_aoef(obj.clip).id,
            tags=[self.tag_adapter.to_aoef(tag).id for tag in obj.tags]
            if obj.tags
            else None,
            annotations=[
                self.sound_event_annotation_adapter.to_aoef(annotation).id
                for annotation in obj.annotations
            ]
            if obj.annotations
            else None,
            notes=[self.note_adapter.to_aoef(note) for note in obj.notes]
            if obj.notes
            else None,
            created_on=obj.created_on,
        )

    def assemble_soundevent(
        self,
        obj: ClipAnnotationsObject,
    ) -> data.ClipAnnotations:
        clip = self.clip_adapter.from_id(obj.clip)
        if clip is None:
            raise ValueError(f"Clip with ID {obj.clip} not found.")

        return data.ClipAnnotations(
            uuid=obj.uuid or uuid4(),
            clip=clip,
            tags=[
                tag
                for tag_id in obj.tags or []
                if (tag := self.tag_adapter.from_id(tag_id)) is not None
            ],
            annotations=[
                annotation
                for annotation_id in obj.annotations or []
                if (
                    annotation := self.sound_event_annotation_adapter.from_id(
                        annotation_id
                    )
                )
                is not None
            ],
            notes=[
                self.note_adapter.to_soundevent(note)
                for note in obj.notes or []
            ],
            created_on=obj.created_on or datetime.datetime.now(),
        )
