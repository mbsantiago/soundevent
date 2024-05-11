import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel

from .note import NoteAdapter
from .recording import RecordingAdapter, RecordingObject
from .tag import TagAdapter, TagObject
from .user import UserAdapter, UserObject
from soundevent import data


class RecordingSetObject(BaseModel):
    """Schema definition for a dataset object in AOEF format."""

    uuid: UUID
    collection_type: Literal["recording_set"] = "recording_set"
    created_on: Optional[datetime.datetime] = None
    recordings: List[RecordingObject]
    tags: Optional[List[TagObject]] = None
    users: Optional[List[UserObject]] = None


class RecordingSetAdapter:
    def __init__(
        self,
        audio_dir: Optional[data.PathLike] = None,
        user_adapter: Optional[UserAdapter] = None,
        tag_adapter: Optional[TagAdapter] = None,
        note_adapter: Optional[NoteAdapter] = None,
        recording_adapter: Optional[RecordingAdapter] = None,
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

    def to_aoef(
        self,
        obj: data.RecordingSet,
    ) -> RecordingSetObject:
        recording_objects = [
            self.recording_adapter.to_aoef(recording)
            for recording in obj.recordings
        ]
        return RecordingSetObject(
            uuid=obj.uuid,
            created_on=obj.created_on,
            users=self.user_adapter.values(),
            tags=self.tag_adapter.values(),
            recordings=recording_objects,
        )

    def to_soundevent(
        self,
        obj: RecordingSetObject,
    ) -> data.RecordingSet:
        for tag in obj.tags or []:
            self.tag_adapter.to_soundevent(tag)

        for user in obj.users or []:
            self.user_adapter.to_soundevent(user)

        recordings = [
            self.recording_adapter.to_soundevent(recording)
            for recording in obj.recordings
        ]

        return data.RecordingSet(
            uuid=obj.uuid or UUID(),
            recordings=recordings,
            created_on=obj.created_on or datetime.datetime.now(),
        )
