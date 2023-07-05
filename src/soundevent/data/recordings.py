"""Recordings.

A recording represents a single audio file, typically an unmodified
file capturing the original audio as recorded by an audio recorder.
Each recording is uniquely identified by a hash or other unique
identifier and is associated with a file path pointing to the audio
file itself. In addition to the audio data, recordings often include
relevant metadata that provides essential information about the
recording.

## Metadata

Recordings can be accompanied by metadata that offers valuable
contextual information. This metadata typically includes the duration
of the recording, sample rate, and the number of audio channels. These
details help in understanding the technical characteristics of the
audio data and ensure accurate processing and analysis.

## Date, Time, and Location Information

To provide temporal and spatial context, recordings can include date
and time information indicating when they were recorded. This allows
for organizing and comparing recordings based on the time of capture.
Latitude and longitude coordinates can also be associated with a
recording, indicating the geographical location where it was recorded.
This information is particularly useful in bioacoustic research and
conservation efforts for understanding species distributions and
habitat characteristics.

## Extending Metadata

Metadata about a recording can be further enriched by attaching
additional tags or features. Tags provide categorical information,
such as the recording site, habitat type, or equipment used.
Features, on the other hand, offer numeric values that quantify
specific characteristics of the recording, such as temperature,
wind speed, or the height of the recording device.

## Textual Notes

Recordings can also have textual notes attached to them, allowing
users to add descriptive information, comments, or discussion points.
These notes provide additional context, insights, or relevant details
that contribute to a deeper understanding of the recording.

The combination of metadata, tags, features, and textual notes
associated with recordings facilitates effective organization,
searchability, and analysis of audio data in bioacoustic research and
related fields.
"""

import datetime
from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel, Field

from soundevent.data.features import Feature
from soundevent.data.notes import Note
from soundevent.data.tags import Tag

__all__ = [
    "Recording",
]


class Recording(BaseModel):
    """Recordings."""

    path: Path
    """The path to the audio file."""

    duration: float
    """The duration of the audio file in seconds."""

    channels: int
    """The number of channels in the audio file."""

    samplerate: int
    """The sample rate of the audio file in Hz."""

    time_expansion: float = 1.0
    """The time expansion factor of the audio file."""

    hash: Optional[str] = None
    """The md5 hash of the audio file."""

    date: Optional[datetime.date] = None
    """The date on which the recording was made."""

    time: Optional[datetime.time] = None
    """The time at which the recording was made."""

    latitude: Optional[float] = None
    """The latitude coordinate of the site of recording."""

    longitude: Optional[float] = None
    """The longitude coordinate of the site of recording."""

    tags: List[Tag] = Field(default_factory=list)
    """The tags associated with the recording."""

    features: List[Feature] = Field(default_factory=list)
    """A list of features associated with the recording."""

    notes: List[Note] = Field(default_factory=list)
    """A list of notes associated with the recording."""

    def __hash__(self):
        """Hash function."""
        return hash(self.hash)
