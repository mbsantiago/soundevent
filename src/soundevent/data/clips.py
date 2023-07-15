"""Clips.

A clip represents a contiguous fragment of a recording, defined by its
start and end times. While recordings serve as the base source of
information, clips are the fundamental unit of work in many analysis
and annotation tasks. When annotating audio or running machine
learning models, the focus is often on working with clips rather than
the entire recording.

## Benefits of Using Clips

There are several reasons for using clips in audio analysis and
annotation tasks. Firstly, working with very long audio files can be
computationally prohibitive for tasks such as visualization and
annotation. Breaking the recording into smaller clips improves
efficiency and enables focused analysis on specific segments of
interest. Secondly, standardizing the duration of clips allows for
consistent and comparable annotations across different recordings. It
provides a consistent unit of analysis, making it easier to interpret
and compare results across various audio data. Lastly, many machine
learning models process audio files in clips, generating predictions
or insights per clip, which further justifies the adoption of the clip
structure.

## Tags and Features

Clips can be annotated by human annotators or processed by machine
learning models to extract valuable information. Annotations can
include the identification of species present within the clip,
descriptions of acoustic characteristics, or any other relevant
categorical information captured by tags. Additionally, numeric
attributes of the acoustic content contained in the clip, such as
spectral features or temporal properties, can be represented as
features attached to the clip.

By utilizing clips as the unit of analysis and annotation, researchers
and practitioners can effectively manage and analyze audio data,
enabling consistent and granular examination of specific segments
within a recording.

"""

from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from soundevent.data.features import Feature
from soundevent.data.recordings import Recording
from soundevent.data.tags import Tag

__all__ = [
    "Clip",
]


class Clip(BaseModel):
    """Clip model."""

    uuid: UUID = Field(default_factory=uuid4)
    """The unique identifier of the clip."""

    recording: Recording
    """The recording that the clip belongs to."""

    start_time: float
    """The start time of the clip in seconds."""

    end_time: float
    """The end time of the clip in seconds."""

    tags: List[Tag] = Field(default_factory=list)
    """List of tags associated with the clip."""

    features: List[Feature] = Field(default_factory=list)
    """List of features associated with the clip."""

    @model_validator(mode="before")
    def validate_times(cls, values):
        """Validate that start_time < end_time."""
        if values["start_time"] > values["end_time"]:
            raise ValueError("start_time must be less than end_time")
        return values

    def __hash__(self):
        """Hash clip object."""
        return hash((self.recording, self.start_time, self.end_time))
