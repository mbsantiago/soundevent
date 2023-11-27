import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from soundevent import data

from .adapters import DataAdapter
from .note import NoteAdapter, NoteObject
from .tag import TagAdapter
from .user import UserAdapter


class RecordingObject(BaseModel):
    """Schema definition for a recording object in AOEF format."""

    uuid: UUID
    path: Path
    duration: float
    channels: int
    samplerate: int
    time_expansion: Optional[float] = None
    hash: Optional[str] = None
    date: Optional[datetime.date] = None
    time: Optional[datetime.time] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    tags: Optional[List[int]] = None
    features: Optional[Dict[str, float]] = None
    notes: Optional[List[NoteObject]] = None
    owners: Optional[List[UUID]] = None
    rights: Optional[str] = None


class RecordingAdapter(DataAdapter[data.Recording, RecordingObject]):
    def __init__(
        self,
        user_adapter: UserAdapter,
        tag_adapter: TagAdapter,
        note_adapter: NoteAdapter,
        audio_dir: Optional[data.PathLike] = None,
    ):
        super().__init__()
        self._user_adapter = user_adapter
        self._tag_adapter = tag_adapter
        self._note_adapter = note_adapter
        self.audio_dir = audio_dir

    def assemble_aoef(
        self,
        obj: data.Recording,
        _: int,
    ) -> RecordingObject:
        tag_ids = [self._tag_adapter.to_aoef(tag).id for tag in obj.tags]

        notes = [self._note_adapter.to_aoef(note) for note in obj.notes]

        owners = [
            self._user_adapter.to_aoef(owner).uuid
            for owner in obj.owners or []
        ]

        path = obj.path
        if self.audio_dir is not None:
            path = Path(obj.path).relative_to(self.audio_dir)

        return RecordingObject(
            uuid=obj.uuid,
            path=path,
            duration=obj.duration,
            channels=obj.channels,
            samplerate=obj.samplerate,
            time_expansion=obj.time_expansion
            if obj.time_expansion != 1.0
            else None,
            hash=obj.hash,
            date=obj.date,
            time=obj.time,
            latitude=obj.latitude,
            longitude=obj.longitude,
            tags=tag_ids if tag_ids else None,
            features={feature.name: feature.value for feature in obj.features}
            if obj.features
            else None,
            notes=notes if notes else None,
            owners=owners,
            rights=obj.rights,
        )

    def assemble_soundevent(
        self, recording: RecordingObject
    ) -> data.Recording:
        tags = [
            tag
            for tag_id in (recording.tags or [])
            if (tag := self._tag_adapter.from_id(tag_id)) is not None
        ]

        notes = [
            self._note_adapter.to_soundevent(note)
            for note in (recording.notes or [])
        ]

        owners = [
            user
            for owner_id in recording.owners or []
            if (user := self._user_adapter.from_id(owner_id)) is not None
        ]

        path = recording.path
        if self.audio_dir is not None:
            path = self.audio_dir / recording.path

        return data.Recording(
            uuid=recording.uuid or uuid4(),
            path=path,
            duration=recording.duration,
            channels=recording.channels,
            samplerate=recording.samplerate,
            time_expansion=recording.time_expansion
            if recording.time_expansion is not None
            else 1.0,
            hash=recording.hash,
            date=recording.date,
            time=recording.time,
            latitude=recording.latitude,
            longitude=recording.longitude,
            tags=tags,
            features=[
                data.Feature(
                    name=name,
                    value=value,
                )
                for name, value in (recording.features or {}).items()
            ],
            notes=notes,
            owners=owners,
            rights=recording.rights,
        )
