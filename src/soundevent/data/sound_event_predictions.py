"""Sound Event Predictions."""

from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.predicted_tags import PredictedTag
from soundevent.data.sound_events import SoundEvent

__all__ = [
    "SoundEventPrediction",
]


class SoundEventPrediction(BaseModel):
    """Predicted Sound Event Class.

    Predicted sound events represent the outcomes of automated methods and
    machine learning models employed to identify sound events within audio
    clips. These predictions provide valuable insights into the presence and
    characteristics of sound events, supporting comprehensive audio analysis.

    Attributes
    ----------
    uuid
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
    """

    uuid: UUID = Field(default_factory=uuid4)
    sound_event: SoundEvent
    score: float = Field(default=1, ge=0, le=1)
    tags: List[PredictedTag] = Field(default_factory=list)

    def __hash__(self) -> int:
        """Return hash value of the predicted sound event."""
        return hash(self.uuid)
