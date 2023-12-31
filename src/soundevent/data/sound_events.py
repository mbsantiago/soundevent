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

__all__ = [
    "SoundEvent",
]


class SoundEvent(BaseModel):
    """Sound Event Class.

    Represents a specific sound event detected within a recording. Each sound
    event is characterized by a unique identifier, the recording in which it
    occurs, its spatial geometry (if available), associated tags, and features.
    Sound events are fundamental entities used for studying and categorizing
    various acoustic phenomena within audio recordings.

    Attributes
    ----------
    uuid
        A unique identifier (UUID) for the sound event.
    geometry
        The spatial geometry locating the sound event within the recording. Can
        include information about the event's position, duration, and frequency
        range.
    features
        A list of features associated with the sound event, offering
        quantitative information about its acoustic properties.
    """

    uuid: UUID = Field(default_factory=uuid4, repr=False)
    geometry: Optional[Geometry]
    recording: Recording
    features: List[Feature] = Field(default_factory=list, repr=False)

    def __hash__(self):
        """Compute the hash of the sound event."""
        return hash(self.uuid)
