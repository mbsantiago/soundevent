"""Matches.

In bioacoustic research, it is often necessary to compare and match sound
events between two different sources of sound event information. The purpose of
matching is to identify and pair sound events from these sources based on some
metric of similarity. The Match object represents the result of this matching
process, providing information about the matched sound events and their
affinity score.

## Matching Process

The matching process involves comparing sound events from a source and target.
This comparison is typically based on a similarity metric that quantifies the
degree of similarity or relatedness between the sound events. The matching
algorithm pairs the closest sound events based on this metric.

## Match Object Structure

The Match object encapsulates the outcome of the matching process. It contains
references to the source and target sound events that were matched, along with
the affinity score that represents the level of similarity between the matched
pair. The affinity score can be used to evaluate the quality or strength of the
match.

## Unmatched Sound Events

It is also important to consider the scenario where some sound events do not
have a matching counterpart in the other source. The Match object can handle
this situation by representing unmatched sound events with a null source or
target sound event. These unmatched sound events provide valuable information,
indicating that certain events were not successfully matched.

By utilizing the Match object, researchers can analyze and understand the
relationships between sound events from different sources, allowing for
comparative studies and insights in bioacoustic research.
"""

from typing import Optional, Sequence
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from soundevent.data.features import Feature
from soundevent.data.sound_event_annotations import SoundEventAnnotation
from soundevent.data.sound_event_predictions import SoundEventPrediction

__all__ = ["Match"]


class Match(BaseModel):
    """Match Class.

    The `Match` class represents the outcome of the matching process in
    bioacoustic research. During this process, sound events from a source and a
    target are compared based on a similarity metric. The matched sound events
    are paired, and the Match object captures these pairs along with their
    affinity scores, indicating the level of similarity between the matched
    events.

    Attributes
    ----------
    source
        The predicted sound event that was matched from the source
        model run.
    target
        The annotation that was matched from the target evaluation set.
    affinity
        The affinity score quantifying the degree of geometric similarity
        between the matched source and target sound events. Affinity
        scores range from 0.0 (no similarity) to 1.0 (perfect match).
        Researchers can use this score to evaluate the strength and
        quality of the match.
    score
        The score of the matched sound event. This score is typically used to
        evaluate the quality of the matched sound event. For example, the score
        could represent the probability of the sound event, or the confidence
        of the model in predicting the sound event.
    metrics
        A list of metrics that were computed for the matched sound event. These
        metrics can be used to evaluate the quality of the matched sound event,
        in addition to the affinity and score.
    """

    uuid: UUID = Field(default_factory=uuid4)
    source: Optional[SoundEventPrediction] = None
    target: Optional[SoundEventAnnotation] = None
    affinity: float = Field(default=0.0, ge=0.0, le=1.0)
    score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    metrics: Sequence[Feature] = Field(default_factory=list)

    @model_validator(mode="before")
    def _validate_match(cls, values):
        """Validate the match."""
        if values.get("source") is None and values.get("target") is None:
            raise ValueError("Match cannot be between two null objects.")
        return values
