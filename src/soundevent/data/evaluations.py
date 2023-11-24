"""Evaluation Model Module.

The `Evaluation` class within the `soundevent.data` package encapsulates the
core components of a bioacoustic evaluation process. This model is central to
assessing the performance of machine learning models in bioacoustic tasks. The
evaluation comprises an `EvaluationSet`, a specific `ModelRun`, computed
metrics, and a set of `EvaluatedExample` instances.
"""
import datetime
from typing import Optional, Sequence
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from soundevent.data.clip_annotations import ClipAnnotations
from soundevent.data.clip_evaluations import ClipEvaluation
from soundevent.data.clip_predictions import ClipPredictions
from soundevent.data.features import Feature

__all__ = [
    "Evaluation",
]


class Evaluation(BaseModel):
    """Evaluation Class."""

    uuid: UUID = Field(default_factory=uuid4, repr=False)
    created_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )
    evaluation_task: str
    clip_annotations: Sequence[ClipAnnotations]
    clip_predictions: Sequence[ClipPredictions]
    clip_evaluations: Sequence[ClipEvaluation] = Field(default_factory=list)
    metrics: Sequence[Feature] = Field(default_factory=list)
    score: Optional[float] = Field(default=None, alias="score")

    @model_validator(mode="after")
    def _check_clip_evaluations(self) -> "Evaluation":
        annotated_clips = {
            annotations.uuid for annotations in self.clip_annotations
        }
        predicted_clips = {
            predictions.uuid for predictions in self.clip_predictions
        }

        for clip_evaluation in self.clip_evaluations:
            if clip_evaluation.uuid not in annotated_clips:
                raise ValueError(
                    f"Clip {clip_evaluation.uuid} not found in "
                    f"annotated clips."
                )
            if clip_evaluation.uuid not in predicted_clips:
                raise ValueError(
                    f"Clip {clip_evaluation.uuid} not found in "
                    f"predicted clips."
                )

        return self
