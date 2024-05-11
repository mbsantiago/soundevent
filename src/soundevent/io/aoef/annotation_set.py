import datetime
from typing import List, Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from .clip import ClipAdapter, ClipObject
from .clip_annotations import ClipAnnotationsAdapter, ClipAnnotationsObject
from .note import NoteAdapter
from .recording import RecordingAdapter, RecordingObject
from .sequence import SequenceAdapter, SequenceObject
from .sequence_annotation import (
    SequenceAnnotationAdapter,
    SequenceAnnotationObject,
)
from .sound_event import SoundEventAdapter, SoundEventObject
from .sound_event_annotation import (
    SoundEventAnnotationAdapter,
    SoundEventAnnotationObject,
)
from .tag import TagAdapter, TagObject
from .user import UserAdapter, UserObject
from soundevent import data


class AnnotationSetObject(BaseModel):
    uuid: UUID
    collection_type: Literal["annotation_set"] = "annotation_set"
    users: Optional[List[UserObject]] = None
    tags: Optional[List[TagObject]] = None
    recordings: Optional[List[RecordingObject]] = None
    sound_events: Optional[List[SoundEventObject]] = None
    sequences: Optional[List[SequenceObject]] = None
    clips: Optional[List[ClipObject]] = None
    sound_event_annotations: Optional[List[SoundEventAnnotationObject]] = None
    sequence_annotations: Optional[List[SequenceAnnotationObject]] = None
    clip_annotations: Optional[List[ClipAnnotationsObject]] = None
    created_on: Optional[datetime.datetime] = None


class AnnotationSetAdapter:
    def __init__(
        self,
        audio_dir: Optional[data.PathLike] = None,
        user_adapter: Optional[UserAdapter] = None,
        tag_adapter: Optional[TagAdapter] = None,
        note_adapter: Optional[NoteAdapter] = None,
        recording_adapter: Optional[RecordingAdapter] = None,
        sound_event_adapter: Optional[SoundEventAdapter] = None,
        sequence_adapter: Optional[SequenceAdapter] = None,
        clip_adapter: Optional[ClipAdapter] = None,
        sound_event_annotations_adapter: Optional[
            SoundEventAnnotationAdapter
        ] = None,
        sequence_annotations_adapter: Optional[
            SequenceAnnotationAdapter
        ] = None,
        clip_annotation_adapter: Optional[ClipAnnotationsAdapter] = None,
    ):
        self.user_adapter = user_adapter or UserAdapter()
        self.tag_adapter = tag_adapter or TagAdapter()
        self.note_adapter = note_adapter or NoteAdapter(self.user_adapter)
        self.recording_adapter = recording_adapter or RecordingAdapter(
            self.user_adapter,
            self.tag_adapter,
            self.note_adapter,
            audio_dir,
        )
        self.sound_event_adapter = sound_event_adapter or SoundEventAdapter(
            self.recording_adapter
        )
        self.sequence_adapter = sequence_adapter or SequenceAdapter(
            self.sound_event_adapter
        )
        self.clip_adapter = clip_adapter or ClipAdapter(self.recording_adapter)
        self.sound_event_annotations_adapter = (
            sound_event_annotations_adapter
            or SoundEventAnnotationAdapter(
                self.user_adapter,
                self.tag_adapter,
                self.note_adapter,
                self.sound_event_adapter,
            )
        )
        self.sequence_annotations_adapter = (
            sequence_annotations_adapter
            or SequenceAnnotationAdapter(
                self.user_adapter,
                self.tag_adapter,
                self.note_adapter,
                self.sequence_adapter,
            )
        )
        self.clip_annotation_adapter = (
            clip_annotation_adapter
            or ClipAnnotationsAdapter(
                self.clip_adapter,
                self.tag_adapter,
                self.note_adapter,
                self.sound_event_annotations_adapter,
                self.sequence_annotations_adapter,
            )
        )

    def to_aoef(
        self,
        obj: data.AnnotationSet,
    ) -> AnnotationSetObject:
        annotated_clips = [
            self.clip_annotation_adapter.to_aoef(clip_annotation)
            for clip_annotation in obj.clip_annotations
        ]
        return AnnotationSetObject(
            uuid=obj.uuid,
            users=self.user_adapter.values(),
            tags=self.tag_adapter.values(),
            recordings=self.recording_adapter.values(),
            clips=self.clip_adapter.values(),
            sound_events=self.sound_event_adapter.values(),
            sound_event_annotations=self.sound_event_annotations_adapter.values(),
            sequences=self.sequence_adapter.values(),
            sequence_annotations=self.sequence_annotations_adapter.values(),
            clip_annotations=annotated_clips,
            created_on=obj.created_on,
        )

    def to_soundevent(
        self,
        obj: AnnotationSetObject,
    ) -> data.AnnotationSet:
        for user in obj.users or []:
            self.user_adapter.to_soundevent(user)

        for tag in obj.tags or []:
            self.tag_adapter.to_soundevent(tag)

        for recording in obj.recordings or []:
            self.recording_adapter.to_soundevent(recording)

        for clip in obj.clips or []:
            self.clip_adapter.to_soundevent(clip)

        for sound_event in obj.sound_events or []:
            self.sound_event_adapter.to_soundevent(sound_event)

        for sequence in obj.sequences or []:
            self.sequence_adapter.to_soundevent(sequence)

        for sound_event_annotation in obj.sound_event_annotations or []:
            self.sound_event_annotations_adapter.to_soundevent(
                sound_event_annotation
            )

        for sequence_annotation in obj.sequence_annotations or []:
            self.sequence_annotations_adapter.to_soundevent(
                sequence_annotation
            )

        annotated_clips = [
            self.clip_annotation_adapter.to_soundevent(clip_annotation)
            for clip_annotation in obj.clip_annotations or []
        ]

        return data.AnnotationSet(
            uuid=obj.uuid or uuid4(),
            clip_annotations=annotated_clips,
            created_on=obj.created_on or datetime.datetime.now(),
        )
