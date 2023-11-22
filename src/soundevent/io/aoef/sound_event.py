from typing import Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from soundevent import data

from .adapters import DataAdapter


class SoundEventObject(BaseModel):
    """Schema definition for a sound event object in AOEF format."""

    id: int
    geometry: Optional[data.Geometry] = None
    uuid: Optional[UUID] = None
    features: Optional[Dict[str, float]] = None


class SoundEventAdapter(DataAdapter[data.SoundEvent, SoundEventObject]):
    def assemble_aoef(
        self, obj: data.SoundEvent, obj_id: int
    ) -> SoundEventObject:
        return SoundEventObject(
            id=obj_id,
            geometry=obj.geometry,
            uuid=obj.uuid,
            features={feature.name: feature.value for feature in obj.features}
            if obj.features
            else None,
        )

    def assemble_soundevent(
        self,
        obj: SoundEventObject,
    ) -> data.SoundEvent:
        return data.SoundEvent(
            uuid=obj.uuid or uuid4(),
            geometry=obj.geometry,
            features=[
                data.Feature(
                    name=name,
                    value=value,
                )
                for name, value in (obj.features or {}).items()
            ],
        )