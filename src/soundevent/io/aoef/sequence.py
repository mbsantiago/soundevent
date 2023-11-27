"""Sequence object in AOEF format."""


from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from soundevent import data

from .adapters import DataAdapter
from .sound_event import SoundEventAdapter


class SequenceObject(BaseModel):
    """Schema definition for a sound event object in AOEF format."""

    uuid: UUID
    sound_events: List[UUID]
    features: Optional[Dict[str, float]] = None
    parent: Optional[UUID] = None


class SequenceAdapter(DataAdapter[data.Sequence, SequenceObject]):
    def __init__(
        self,
        soundevent_adapter: SoundEventAdapter,
    ):
        super().__init__()
        self.soundevent_adapter = soundevent_adapter

    def assemble_aoef(self, obj: data.Sequence, _: int) -> SequenceObject:
        parent = None
        if obj.parent:
            parent = self.to_aoef(obj.parent).uuid

        sound_events = [
            self.soundevent_adapter.to_aoef(sound_event).uuid
            for sound_event in obj.sound_events
        ]

        return SequenceObject(
            uuid=obj.uuid,
            sound_events=sound_events,
            parent=parent,
            features={feature.name: feature.value for feature in obj.features}
            if obj.features
            else None,
        )

    def assemble_soundevent(
        self,
        obj: SequenceObject,
    ) -> data.Sequence:
        sound_events = [
            sound_event
            for sound_event_id in obj.sound_events
            if (sound_event := self.soundevent_adapter.from_id(sound_event_id))
            is not None
        ]

        return data.Sequence(
            uuid=obj.uuid or uuid4(),
            sound_events=sound_events,
            parent=self.from_id(obj.parent) if obj.parent else None,
            features=[
                data.Feature(
                    name=name,
                    value=value,
                )
                for name, value in (obj.features or {}).items()
            ],
        )
