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
    """Predicted Sound Event Class.

    Predicted sound events represent the outcomes of automated methods and
    machine learning models employed to identify sound events within audio
    clips. These predictions provide valuable insights into the presence and
    characteristics of sound events, supporting comprehensive audio analysis.

    Attributes
    ----------
    id
        A unique identifier for the prediction, automatically generated upon
        creation. This identifier distinguishes each prediction, facilitating
        reference and management.
    sound_event
        The predicted sound event captured by the automated method or machine
        learning model. This encapsulates details such as the sound event's
        temporal properties, and other essential characteristics.
    score
        A probability score indicating the confidence of the prediction. This
        score reflects the certainty of the event's identification within the
        clip. Researchers leverage these scores to assess the reliability and
        accuracy of the predictions, enabling further analysis and evaluation.
    tags
        A list of predicted tags associated with the sound event. Predicted
        tags provide semantic labels that offer insights into the nature and
        characteristics of the event. Each tag is assigned its own probability
        score, indicating the model's confidence in the relevance of the tag to
        the event. These scores assist researchers in understanding the
        significance and reliability of the predicted tags.
    features
        A list of acoustic features capturing various characteristics and
        properties of the predicted sound event. These features, obtained
        through automated analysis methods, enable a more comprehensive
        understanding and analysis of the event's acoustic content.
    """

    id: UUID = Field(default_factory=uuid4)
    sound_event: SoundEvent
    score: float = Field(default=1, ge=0, le=1)
    tags: List[PredictedTag] = Field(default_factory=list)
    features: List[Feature] = Field(default_factory=list)

    def __hash__(self) -> int:
        """Return hash value of the predicted sound event."""
        return hash(self.id)
