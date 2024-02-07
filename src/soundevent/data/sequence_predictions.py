"""Sequence Prediction Class."""

from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.predicted_tags import PredictedTag
from soundevent.data.sequences import Sequence

__all__ = [
    "SequencePrediction",
]


class SequencePrediction(BaseModel):
    """A class representing a sequence prediction.

    Attributes
    ----------
    uuid
        A unique identifier for the prediction.
    sequence
        The sequence being predicted.
    score
        A score between 0 and 1 indicating the confidence in the prediction.
    tags
        List of tags attached to the sequence providing semantic information.
    """

    uuid: UUID = Field(default_factory=uuid4)
    sequence: Sequence
    score: float = Field(default=1, ge=0, le=1)
    tags: List[PredictedTag] = Field(default_factory=list)
