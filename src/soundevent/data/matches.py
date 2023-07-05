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

from typing import Optional

from pydantic import BaseModel, Field

from soundevent.data.sound_events import SoundEvent


class Match(BaseModel):
    """Match."""

    source: Optional[SoundEvent]
    """Source sound event."""

    target: Optional[SoundEvent]
    """Target sound event."""

    affinity: float = Field(default=0.0, ge=0.0, le=1.0)
    """Affinity between the source and target sound events."""
