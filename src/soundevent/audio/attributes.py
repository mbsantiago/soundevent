"""Definition of common attributes for audio objects."""

from enum import Enum

__all__ = [
    "AudioAttrs",
]


class AudioAttrs(str, Enum):
    samplerate = "samplerate"

    recording_id = "recording_id"

    clip_id = "clip_id"

    path = "path"
