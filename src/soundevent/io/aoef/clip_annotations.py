import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from .adapters import DataAdapter
from .clip import ClipAdapter
from .note import NoteAdapter, NoteObject
from .sequence_annotation import SequenceAnnotationAdapter
from .sound_event_annotation import SoundEventAnnotationAdapter
from .tag import TagAdapter
from soundevent import data


class ClipAnnotationsObject(BaseModel):
    """Schema definition for the clip annotations object in AOEF format."""

    uuid: UUID
    clip: UUID
    tags: Optional[List[int]] = None
    sound_events: Optional[List[UUID]] = None
    sequences: Optional[List[UUID]] = None
    notes: Optional[List[NoteObject]] = None
    created_on: Optional[datetime.datetime] = None


class ClipAnnotationsAdapter(
    DataAdapter[data.ClipAnnotation, ClipAnnotationsObject, UUID, UUID]
):
    def __init__(
        self,
        clip_adapter: ClipAdapter,
        tag_adapter: TagAdapter,
        note_adapter: NoteAdapter,
        sound_event_annotation_adapter: SoundEventAnnotationAdapter,
        sequence_annotation_adapter: SequenceAnnotationAdapter,
    ):
        super().__init__()
        self.clip_adapter = clip_adapter
        self.tag_adapter = tag_adapter
        self.note_adapter = note_adapter
        self.sound_event_annotation_adapter = sound_event_annotation_adapter
        self.sequence_annotation_adapter = sequence_annotation_adapter

    def assemble_aoef(
        self,
        obj: data.ClipAnnotation,
        obj_id: UUID,
    ) -> ClipAnnotationsObject:
        return ClipAnnotationsObject(
            uuid=obj.uuid,
            clip=self.clip_adapter.to_aoef(obj.clip).uuid,
            tags=(
                [self.tag_adapter.to_aoef(tag).id for tag in obj.tags]
                if obj.tags
                else None
            ),
            sound_events=(
                [
                    self.sound_event_annotation_adapter.to_aoef(
                        annotation
                    ).uuid
                    for annotation in obj.sound_events
                ]
                if obj.sound_events
                else None
            ),
            sequences=(
                [
                    self.sequence_annotation_adapter.to_aoef(annotation).uuid
                    for annotation in obj.sequences
                ]
                if obj.sequences
                else None
            ),
            notes=(
                [self.note_adapter.to_aoef(note) for note in obj.notes]
                if obj.notes
                else None
            ),
            created_on=obj.created_on,
        )

    def assemble_soundevent(
        self,
        obj: ClipAnnotationsObject,
    ) -> data.ClipAnnotation:
        clip = self.clip_adapter.from_id(obj.clip)
        if clip is None:
            raise ValueError(f"Clip with ID {obj.clip} not found.")

        return data.ClipAnnotation(
            uuid=obj.uuid or uuid4(),
            clip=clip,
            tags=[
                tag
                for tag_id in obj.tags or []
                if (tag := self.tag_adapter.from_id(tag_id)) is not None
            ],
            sound_events=[
                se_ann
                for annotation_id in obj.sound_events or []
                if (
                    se_ann := self.sound_event_annotation_adapter.from_id(
                        annotation_id
                    )
                )
                is not None
            ],
            sequences=[
                seq_ann
                for annotation_id in obj.sequences or []
                if (
                    seq_ann := self.sequence_annotation_adapter.from_id(
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
