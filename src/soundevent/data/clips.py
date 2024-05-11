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

## Features

Numeric attributes of the acoustic content contained in the clip, such as
spectral features or temporal properties, can be represented as features
attached to the clip.

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

__all__ = [
    "Clip",
]


class Clip(BaseModel):
    """Clip Class.

    The `Clip` class represents a specific segment of an audio recording within
    the context of bioacoustic research. Clips provide isolated and manageable
    portions of audio data, essential for analysis, annotation, and machine
    learning tasks.

    Attributes
    ----------
    uuid : UUID, optional
        The unique identifier of the clip, automatically generated upon
        creation. This identifier distinguishes the clip from others and is
        crucial for referencing and management purposes.
    recording : Recording
        An instance of the `Recording` class representing the larger audio
        recording that the clip belongs to. Clips are extracted from recordings
        and serve as individual units for analysis. The recording provides
        essential context for understanding the origin and source of the audio
        data.
    start_time : float
        The start time of the clip in seconds, indicating the beginning point
        of the segment within the recording's timeline. Start time is essential
        for accurate temporal positioning and alignment of the clip within the
        context of the original recording.
    end_time : float
        The end time of the clip in seconds, representing the conclusion of the
        segment within the recording's timeline. End time provides clear
        boundaries for the duration of the clip, aiding in precise temporal
        delineation and analysis of the audio content.
    features : List[Feature], optional
        A list of `Feature` instances representing computed features or
        descriptors associated with the clip. Features provide quantitative and
        qualitative insights into the audio content, allowing for advanced
        analysis and machine learning applications. These features serve as
        valuable inputs for algorithms and models, enhancing the depth of
        analysis and interpretation.
    """

    uuid: UUID = Field(default_factory=uuid4)
    recording: Recording
    start_time: float
    end_time: float
    features: List[Feature] = Field(default_factory=list)

    @model_validator(mode="before")
    def _validate_times(cls, values):
        """Validate that start_time < end_time."""
        if values["start_time"] > values["end_time"]:
            raise ValueError("start_time must be less than end_time")
        return values

    @property
    def duration(self) -> float:
        """Return the duration of the clip."""
        return self.end_time - self.start_time
