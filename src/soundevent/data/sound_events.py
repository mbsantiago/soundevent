"""Sound events.

The `soundevent` package is designed to focus on the analysis of sound
events, which play a crucial role in bioacoustic research. Sound
events refer to distinct and discernible sounds within a recording
that are of particular interest for analysis. A recording can contain
multiple sound events or none at all, depending on the audio content.

## Identification and Localization

Human annotators are responsible for identifying and locating sound
events within a recording. This process involves careful listening and
precise determination of the sound event's location. Various methods
can be employed to specify the location, such as indicating the
event's onset timestamp, start and end times, or providing detailed
information about the associated time and frequency regions.

## Tags and Semantic Information

To provide meaningful context, sound events can be enriched with tags,
which are labels attached to the events. These tags offer semantic
information about the sound events, including the species responsible
for the sound, the behavior exhibited by the sound emitter, or even
the specific syllable within a vocalization. Tags aid in organizing
and categorizing sound events, enabling more efficient analysis and
interpretation.

## Features and Numerical Descriptors

In addition to tags, sound events can be characterized by features,
which are numerical descriptors attached to the events. These features
provide quantitative information about the sound events, such as
duration, bandwidth, peak frequency, and other detailed measurements
that can be extracted using advanced techniques like deep learning
models. Features offer valuable insights into the acoustic properties
of the sound events.
"""

from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.features import Feature
from soundevent.data.geometries import Geometry
from soundevent.data.recordings import Recording
from soundevent.data.tags import Tag

__all__ = [
    "SoundEvent",
]


class SoundEvent(BaseModel):
    """Sound events."""

    uuid: UUID = Field(default_factory=uuid4, repr=False)
    """The UUID of the sound event."""

    recording: Recording = Field(..., repr=False)
    """The recording containing the sound event."""

    geometry: Optional[Geometry]
    """The geometry locating the sound event within the recording."""

    tags: List[Tag] = Field(default_factory=list, repr=False)
    """The tags associated with the sound event."""

    features: List[Feature] = Field(default_factory=list, repr=False)
    """The features associated with the sound event."""

    def __hash__(self):
        """Compute the hash of the sound event."""
        return hash(self.uuid)
