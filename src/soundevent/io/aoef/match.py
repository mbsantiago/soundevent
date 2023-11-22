from typing import Dict, Optional, Tuple
from uuid import UUID

from pydantic import BaseModel

from soundevent import data

from .adapters import DataAdapter
from .sound_event_annotation import SoundEventAnnotationAdapter
from .sound_event_prediction import SoundEventPredictionAdapter


class MatchObject(BaseModel):
    id: int
    source: Optional[int] = None
    target: Optional[int] = None
    affinity: float
    score: Optional[float] = None
    metrics: Optional[Dict[str, float]] = None


class MatchAdapter(DataAdapter[data.Match, MatchObject]):  # type: ignore
    def __init__(
        self,
        sound_event_annotation_adapter: SoundEventAnnotationAdapter,
        sound_event_prediction_adapter: SoundEventPredictionAdapter,
    ):
        super().__init__()
        self.sound_event_annotation_adapter = sound_event_annotation_adapter
        self.sound_event_prediction_adapter = sound_event_prediction_adapter

    def assemble_aoef(
        self,
        obj: data.Match,
        obj_id: int,
    ) -> MatchObject:
        source = None
        if obj.source is not None:
            prediction = self.sound_event_prediction_adapter.to_aoef(
                obj.source
            )
            source = prediction.id if prediction is not None else None

        target = None
        if obj.target is not None:
            annotation = self.sound_event_annotation_adapter.to_aoef(
                obj.target
            )
            target = annotation.id if annotation is not None else None

        return MatchObject(
            id=obj_id,
            source=source,
            target=target,
            affinity=obj.affinity,
            score=obj.score,
            metrics={metrics.name: metrics.value for metrics in obj.metrics}
            if obj.metrics
            else None,
        )

    def assemble_soundevent(
        self,
        obj: MatchObject,
    ) -> data.Match:
        source = None
        if obj.source is not None:
            source = self.sound_event_prediction_adapter.from_id(obj.source)

        target = None
        if obj.target is not None:
            target = self.sound_event_annotation_adapter.from_id(obj.target)

        return data.Match(
            source=source,
            target=target,
            affinity=obj.affinity,
            score=obj.score,
            metrics=[
                data.Feature(
                    name=name,
                    value=value,
                )
                for name, value in (obj.metrics or {}).items()
            ],
        )

    @classmethod
    def _get_key(
        cls, obj: data.Match
    ) -> Tuple[Optional[UUID], Optional[UUID]]:
        left = obj.source.uuid if obj.source is not None else None
        right = obj.target.uuid if obj.target is not None else None
        return (left, right)
