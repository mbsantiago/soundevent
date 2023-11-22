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

from soundevent.data.annotation_sets import AnnotationSet
from soundevent.data.clip_evaluations import ClipEvaluation
from soundevent.data.features import Feature
from soundevent.data.prediction_sets import PredictionSet

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

    annotation_set: AnnotationSet
    prediction_set: PredictionSet

    metrics: Sequence[Feature] = Field(default_factory=list)
    evaluated_clips: Sequence[ClipEvaluation] = Field(default_factory=list)
    score: Optional[float] = Field(default=None, alias="score")

    @model_validator(mode="after")  # type: ignore
    def _check_evaluated_samples_belong_to_set(self):
        """Check that all evaluated examples belong to the evaluation set."""
        evaluation_set_examples = {
            example.uuid for example in self.annotation_set.clip_annotations
        }
        if any(
            evaluated.annotations.uuid not in evaluation_set_examples
            for evaluated in self.evaluated_clips
        ):
            raise ValueError(
                "Not all evaluated examples belong to the evaluation set."
            )
        return self
