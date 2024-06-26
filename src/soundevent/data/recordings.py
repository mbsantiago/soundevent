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
import os
from pathlib import Path
from typing import List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.features import Feature
from soundevent.data.notes import Note
from soundevent.data.tags import Tag
from soundevent.data.users import User

__all__ = [
    "Recording",
    "PathLike",
]


PathLike = Union[os.PathLike, str]
"""PathLike: A type alias for a path-like object."""


class Recording(BaseModel):
    """Recording Class.

    Representing an audio recording in bioacoustic research, recordings embody
    single files in their raw, unaltered state, typically as generated by
    recording devices. They serve as the foundational material upon which
    bioacoustic research is conducted. Each recording is characterized by a
    unique identifier, file path, duration, number of channels, sample rate,
    time expansion factor (if applicable), hash, recording date, time,
    geographic coordinates, associated tags, features, and notes

    Attributes
    ----------
    uuid
        A unique identifier for the recording.
    path
        The file path to the audio recording.
    duration
        The duration of the audio file in seconds. This duration is adjusted by
        the time expansion factor if the audio file is time expanded, providing
        the real duration of the recorded audio.
    channels
        The number of channels in the audio file.
    samplerate
        The sample rate of the audio file in Hz. Similar to duration, the
        sample rate is adjusted by the time expansion factor if the audio file
        is time expanded, representing the real sample rate of the recorded
        audio.
    time_expansion
        The time expansion factor of the audio file. Default is 1.0, indicating
        no time expansion.
    hash
        The md5 hash of the audio file. Default is None.
    date
        The date on which the recording was made. Default is None.
    time
        The time at which the recording was made. Default is None.
    latitude
        The latitude coordinate of the site of recording. Default is None.
    longitude
        The longitude coordinate of the site of recording. Default is None.
    tags
        A list of tags associated with the recording. Default is an empty list.
    features
        A list of features associated with the recording. Default is an empty
        list.
    notes : List[Note]
        A list of notes associated with the recording. Default is an empty
        list.

    Notes
    -----
    When dealing with time-expanded recordings, adjustments are made to both
    the duration and sample rate based on the time expansion factor. As a
    result, the duration and sample rate stored in the Recording object may
    deviate from the values derived from the file metadata.

    A time-expanded recording is one that has been either slowed down or sped
    up, typically to facilitate the playback and analysis of audio data. In
    these cases, although the audio was originally captured at a specific
    sample rate, the resulting audio file exhibits a different sample rate due
    to the time expansion process. The time expansion factor represents the
    ratio of the original sample rate to the sample rate of the time-expanded
    recording.

    Since the actual sample rate used to capture the audio differs from the
    stored sample rate in the audio file, we have chosen to store the true
    sample rate in the Recording object. This ensures that the Recording object
    accurately reflects the sample rate at which the audio was originally
    captured.
    """

    uuid: UUID = Field(default_factory=uuid4, repr=False)
    path: Path
    duration: float
    channels: int
    samplerate: int
    time_expansion: float = 1.0
    hash: Optional[str] = Field(default=None, repr=False)
    date: Optional[datetime.date] = Field(default=None, repr=False)
    time: Optional[datetime.time] = Field(default=None, repr=False)
    latitude: Optional[float] = Field(default=None, repr=False)
    longitude: Optional[float] = Field(default=None, repr=False)
    tags: List[Tag] = Field(default_factory=list, repr=False)
    features: List[Feature] = Field(default_factory=list, repr=False)
    notes: List[Note] = Field(default_factory=list, repr=False)
    owners: List[User] = Field(default_factory=list, repr=False)
    rights: Optional[str] = None

    @classmethod
    def from_file(
        cls,
        path: PathLike,
        time_expansion: float = 1,
        compute_hash: bool = True,
        **kwargs,
    ) -> "Recording":
        """Create a recording object from a file.

        This function does not load the audio data itself, but rather
        extracts the metadata from the file and creates a recording
        object with the appropriate metadata.

        Parameters
        ----------
        path
            The path to the audio file.
        time_expansion
            The time expansion factor of the audio file, by default 1.
        compute_hash
            Whether to compute the md5 hash of the audio file, by default True.
            If you are loading a large number of recordings, you might want
            to set this to False to speed up the loading process.
        **kwargs
            Additional keyword arguments to pass to the constructor.

        Returns
        -------
        Recording
            The recording object.
        """
        from soundevent.audio.media_info import (
            compute_md5_checksum,
            get_media_info,
        )

        media_info = get_media_info(path)

        hash = None
        if compute_hash:
            hash = compute_md5_checksum(path)

        return cls(
            path=Path(path),
            hash=hash,
            duration=media_info.duration_s / time_expansion,
            channels=media_info.channels,
            samplerate=int(media_info.samplerate_hz * time_expansion),
            time_expansion=time_expansion,
            **kwargs,
        )
