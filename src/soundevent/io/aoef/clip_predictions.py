from typing import Dict, List, Optional, Tuple
from uuid import UUID

from pydantic import BaseModel

from soundevent import data

from .adapters import DataAdapter
from .clip import ClipAdapter
from .sound_event_prediction import SoundEventPredictionAdapter
from .tag import TagAdapter


class ClipPredictionsObject(BaseModel):
    id: int
    uuid: UUID
    clip: int
    sound_events: Optional[List[int]] = None
    tags: Optional[List[Tuple[int, float]]] = None
    features: Optional[Dict[str, float]] = None


class ClipPredictionsAdapter(
    DataAdapter[data.ClipPredictions, ClipPredictionsObject]
):
    def __init__(
        self,
        clip_adapter: ClipAdapter,
        sound_event_prediction_adapter: SoundEventPredictionAdapter,
        tag_adapter: TagAdapter,
    ):
        super().__init__()
        self.clip_adapter = clip_adapter
        self.sound_event_prediction_adapter = sound_event_prediction_adapter
        self.tag_adapter = tag_adapter

    def assemble_aoef(
        self,
        obj: data.ClipPredictions,
        obj_id: int,
    ) -> ClipPredictionsObject:
        return ClipPredictionsObject(
            id=obj_id,
            uuid=obj.uuid,
            clip=self.clip_adapter.to_aoef(obj.clip).id,
            sound_events=[
                self.sound_event_prediction_adapter.to_aoef(sound_event).id
                for sound_event in obj.sound_events
            ]
            if obj.sound_events
            else None,
            tags=[
                (tag.id, predicted_tag.score)
                for predicted_tag in obj.tags
                if (tag := self.tag_adapter.to_aoef(predicted_tag.tag))
                is not None
            ]
            if obj.tags
            else None,
            features={feature.name: feature.value for feature in obj.features}
            if obj.features is not None
            else None,
        )

    def assemble_soundevent(
        self,
        obj: ClipPredictionsObject,
    ) -> data.ClipPredictions:
        clip = self.clip_adapter.from_id(obj.clip)

        if clip is None:
            raise ValueError(f"Clip with ID {obj.clip} not found.")

        return data.ClipPredictions(
            uuid=obj.uuid,
            clip=clip,
            sound_events=[
                prediction
                for sound_event in obj.sound_events or []
                if (
                    prediction := self.sound_event_prediction_adapter.from_id(
                        sound_event
                    )
                )
                is not None
            ],
            tags=[
                data.PredictedTag(
                    tag=tag,
                    score=score,
                )
                for tag_id, score in obj.tags or {}
                if (tag := self.tag_adapter.from_id(tag_id)) is not None
            ],
            features=[
                data.Feature(name=name, value=value)
                for name, value in (obj.features or {}).items()
            ],
        )
