"""Model Run Module."""

from typing import Optional

from soundevent.data.prediction_sets import PredictionSet

__all__ = [
    "ModelRun",
]


class ModelRun(PredictionSet):
    name: str
    version: Optional[str] = None
    description: Optional[str] = None
