"""Predicted Sound Events.

Predicted sound events play a crucial role in the field of audio
analysis, where machine learning models and automated methods are
employed to identify sound events within audio clips. These predicted
sound events represent the outputs of these methods, providing
valuable insights into the presence and characteristics of sound
events.

## Probability Scores and Confidence

When a machine learning model or automated method identifies a sound
event, it assigns a probability score to indicate its confidence in
the presence of that event within the clip. This probability score
reflects the degree of certainty associated with the event's
identification. Researchers can utilize these scores to assess the
reliability and accuracy of the predicted sound events, enabling
further analysis and evaluation.

## Predicted Tags

Predicted sound events can be enriched with additional information
through the inclusion of predicted tags. Each predicted sound event
can have multiple predicted tags associated with it, providing
semantic labels that offer insights into the nature and
characteristics of the event. Each predicted tag is assigned its own
probability score, which reflects the confidence of the model in the
relevance of the tag to the event. These scores assist researchers in
understanding the significance and reliability of the predicted tags.

## Acoustic Features

Automated analysis methods often yield acoustic features as a result
of their processing. These features capture various characteristics
and properties of the predicted sound events. Researchers can attach
these acoustic features to the predicted sound events, enabling a
more comprehensive understanding and analysis of the events' acoustic
content.

"""
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.features import Feature
from soundevent.data.predicted_tags import PredictedTag
from soundevent.data.sound_events import SoundEvent

__all__ = [
    "PredictedSoundEvent",
]


class PredictedSoundEvent(BaseModel):
    """Predicted sound event."""

    id: UUID = Field(default_factory=uuid4)
    """The unique identifier of the prediction."""

    sound_event: SoundEvent
    """Predicted sound event."""

    score: float = Field(default=1, ge=0, le=1)
    """The probability score of the predicted sound event."""

    tags: List[PredictedTag] = Field(default_factory=list)
    """List of predicted tags associated with the prediction."""

    features: List[Feature] = Field(default_factory=list)
    """List of features associated with the prediction."""

    def __hash__(self) -> int:
        """Return hash value of the predicted sound event."""
        return hash(self.id)
