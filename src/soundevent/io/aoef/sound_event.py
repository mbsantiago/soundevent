from typing import Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from .adapters import DataAdapter
from .recording import RecordingAdapter
from soundevent import data


class SoundEventObject(BaseModel):
    """Schema definition for a sound event object in AOEF format."""

    uuid: UUID
    recording: UUID
    geometry: Optional[data.Geometry] = None
    features: Optional[Dict[str, float]] = None


class SoundEventAdapter(
    DataAdapter[data.SoundEvent, SoundEventObject, UUID, UUID]
):
    def __init__(
        self,
        recording_adapter: RecordingAdapter,
    ):
        super().__init__()
        self.recording_adapter = recording_adapter

    def assemble_aoef(
        self,
        obj: data.SoundEvent,
        obj_id: UUID,
    ) -> SoundEventObject:
        return SoundEventObject(
            geometry=obj.geometry,
            uuid=obj.uuid,
            recording=self.recording_adapter.to_aoef(obj.recording).uuid,
            features=(
                {
                    data.key_from_term(feature.term): feature.value
                    for feature in obj.features
                }
                if obj.features
                else None
            ),
        )

    def assemble_soundevent(
        self,
        obj: SoundEventObject,
    ) -> data.SoundEvent:
        recording = self.recording_adapter.from_id(obj.recording)

        if recording is None:
            raise ValueError(f"Recording with ID {obj.recording} not found.")

        return data.SoundEvent(
            uuid=obj.uuid or uuid4(),
            geometry=obj.geometry,
            recording=recording,
            features=[
                data.Feature(
                    term=data.term_from_key(name),
                    value=value,
                )
                for name, value in (obj.features or {}).items()
            ],
        )
