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

from pydantic import BaseModel, Field

from soundevent.data.clip_evaluations import ClipEvaluation
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
    clip_evaluations: Sequence[ClipEvaluation] = Field(default_factory=list)
    metrics: Sequence[Feature] = Field(default_factory=list)
    score: Optional[float] = Field(default=None, alias="score")
