from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from soundevent import data

from .adapters import DataAdapter
from .clip_annotations import ClipAnnotationsAdapter
from .clip_predictions import ClipPredictionsAdapter
from .match import MatchAdapter
from .note import NoteAdapter


class ClipEvaluationObject(BaseModel):
    uuid: UUID
    annotations: UUID
    predictions: UUID
    matches: Optional[List[UUID]] = None
    metrics: Optional[Dict[str, float]] = None
    score: Optional[float] = None


class ClipEvaluationAdapter(
    DataAdapter[data.ClipEvaluation, ClipEvaluationObject]
):
    def __init__(
        self,
        clip_annotations_adapter: ClipAnnotationsAdapter,
        clip_predictions_adapter: ClipPredictionsAdapter,
        note_adapter: NoteAdapter,
        match_adapter: MatchAdapter,
    ):
        super().__init__()
        self.clip_annotations_adapter = clip_annotations_adapter
        self.clip_predictions_adapter = clip_predictions_adapter
        self.note_adapter = note_adapter
        self.match_adapter = match_adapter

    def assemble_aoef(
        self,
        obj: data.ClipEvaluation,
        _: int,
    ) -> ClipEvaluationObject:
        annotations = self.clip_annotations_adapter.to_aoef(obj.annotations)
        predictions = self.clip_predictions_adapter.to_aoef(obj.predictions)

        return ClipEvaluationObject(
            uuid=obj.uuid,
            annotations=annotations.uuid,
            predictions=predictions.uuid,
            matches=[
                self.match_adapter.to_aoef(match).uuid for match in obj.matches
            ]
            if obj.matches
            else None,
            metrics={metrics.name: metrics.value for metrics in obj.metrics}
            if obj.metrics
            else None,
            score=obj.score,
        )

    def assemble_soundevent(
        self,
        obj: ClipEvaluationObject,
    ) -> data.ClipEvaluation:
        annotations = self.clip_annotations_adapter.from_id(obj.annotations)
        predictions = self.clip_predictions_adapter.from_id(obj.predictions)

        if annotations is None:
            raise ValueError(
                f"Clip annotations with ID {obj.annotations} not found."
            )

        if predictions is None:
            raise ValueError(
                f"Clip predictions with ID {obj.predictions} not found."
            )

        matches = [
            match
            for match_id in obj.matches or []
            if (match := self.match_adapter.from_id(match_id)) is not None
        ]

        return data.ClipEvaluation(
            uuid=obj.uuid or uuid4(),
            annotations=annotations,
            predictions=predictions,
            matches=matches,
            metrics=[
                data.Feature(name=name, value=value)
                for name, value in (obj.metrics or {}).items()
            ],
            score=obj.score,
        )
