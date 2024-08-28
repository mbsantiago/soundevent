from typing import Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from .adapters import DataAdapter
from .recording import RecordingAdapter
from soundevent import data


class ClipObject(BaseModel):
    """Schema definition for a clip object in AOEF format."""

    uuid: UUID
    recording: UUID
    start_time: float
    end_time: float
    features: Optional[Dict[str, float]] = None


class ClipAdapter(DataAdapter[data.Clip, ClipObject, UUID, UUID]):
    def __init__(
        self,
        recording_adapter: RecordingAdapter,
    ):
        super().__init__()
        self.recording_adapter = recording_adapter

    def assemble_aoef(self, obj: data.Clip, obj_id: UUID) -> ClipObject:
        return ClipObject(
            recording=self.recording_adapter.to_aoef(obj.recording).uuid,
            start_time=obj.start_time,
            end_time=obj.end_time,
            uuid=obj.uuid,
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
        obj: ClipObject,
    ) -> data.Clip:
        recording = self.recording_adapter.from_id(obj.recording)

        if recording is None:
            raise ValueError(f"Recording with ID {obj.recording} not found.")

        return data.Clip(
            recording=recording,
            start_time=obj.start_time,
            end_time=obj.end_time,
            uuid=obj.uuid or uuid4(),
            features=(
                [
                    data.Feature(
                        term=data.term_from_key(name),
                        value=value,
                    )
                    for name, value in obj.features.items()
                ]
                if obj.features
                else []
            ),
        )
