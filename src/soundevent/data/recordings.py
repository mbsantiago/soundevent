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

from pydantic import BaseModel, ConfigDict, Field

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
    """Represents an audio recording in bioacoustic research.

    This class models raw, unaltered audio files as captured by recording
    devices. Recordings are fundamental to bioacoustic research and are
    identified by various metadata, including:

    * Unique identifier
    * File path
    * Duration
    * Number of channels
    * Sample rate
    * Time expansion factor
    * Hash
    * Geographic coordinates
    * Tags, features, and notes

    Notes
    -----
    For time-expanded audio (slowed down or sped up), the `duration` and
    `sample_rate` reflect the **original recording values**, not the modified
    values in the file. This ensures accuracy in representing the audio's true
    capture conditions.
    """

    model_config = ConfigDict(extra="allow")

    uuid: UUID = Field(
        default_factory=uuid4,
        serialization_alias="dcterms:identifier",
        title="Identifier",
        description="An unambiguous reference to the resource within a given context.",
        repr=False,
        json_schema_extra={
            "$id": "http://purl.org/dc/terms/identifier",
        },
    )
    """A unique identifier for the recording."""

    path: Path = Field(
        title="Path",
        description="The path to the audio file.",
        repr=True,
    )
    """The file path to the audio recording."""

    duration: float = Field(
        title="Duration",
        serialization_alias="ac:mediaDuration",
        description="The duration of the audio file in seconds.",
        repr=False,
        json_schema_extra={
            "$id": "http://rs.tdwg.org/ac/terms/mediaDuration",
        },
    )
    """The duration of the audio file in seconds. 

    This duration is adjusted by the time expansion factor if the audio file is
    time expanded, providing the real duration of the recorded audio.
    """

    channels: int = Field(
        title="Channels",
        serialization_alias="mo:channels",
        description="The number of channels in the audio file.",
        repr=False,
        json_schema_extra={"$id": "http://purl.org/ontology/mo/channels"},
    )
    """The number of channels in the audio file."""

    samplerate: int = Field(
        title="Sample Rate",
        serialization_alias="mo:sample_rate",
        description="The sample rate of the audio file in Hz.",
        repr=False,
        json_schema_extra={"$id": "http://purl.org/ontology/mo/sample_rate"},
    )
    """The sample rate of the audio file in Hz. 

    Similar to duration, the sample rate is adjusted by the time expansion
    factor if the audio file is time expanded, representing the real sample
    rate of the recorded audio.
    """

    time_expansion: float = Field(
        default=1.0,
        serialization_alias="ac:mediaSpeed",
        title="Media Speed",
        description="The decimal fraction representing the natural speed over the encoded speed.",
        repr=False,
        json_schema_extra={"$id": "http://rs.tdwg.org/ac/terms/mediaSpeed"},
    )
    """The time expansion factor of the audio file.

    Default is 1.0, indicating no time expansion.
    """

    hash: Optional[str] = Field(
        default=None,
        serialization_alias="ac:hashValue",
        title="Hash",
        description="The value computed by a hash function applied to the media that will be delivered at the access point.",
        repr=False,
        json_schema_extra={"$id": "http://rs.tdwg.org/ac/terms/hashValue"},
    )
    """The md5 hash of the audio file. 

    Default is None.
    """

    date: Optional[datetime.date] = Field(
        default=None,
        repr=False,
        deprecated=False,
    )
    """The date on which the recording was made. 

    Default is None.
    """

    time: Optional[datetime.time] = Field(
        default=None,
        repr=False,
        deprecated=False,
    )
    """The time at which the recording was made. 

    Default is None.
    """

    latitude: Optional[float] = Field(
        default=None,
        serialization_alias="dwc:decimalLatitude",
        title="Decimal Latitude",
        description="The geographic latitude (in decimal degrees, using the spatial reference system given in dwc:geodeticDatum) of the geographic center of a dcterms:Location. Positive values are north of the Equator, negative values are south of it. Legal values lie between -90 and 90, inclusive.",
        repr=False,
        json_schema_extra={
            "$id": "http://rs.tdwg.org/dwc/terms/decimalLatitude"
        },
    )
    """The latitude coordinate of the site of recording. 

    Default is None.
    """

    longitude: Optional[float] = Field(
        default=None,
        serialization_alias="dwc:decimalLongitude",
        title="Decimal Longitude",
        description="The geographic longitude (in decimal degrees, using the spatial reference system given in dwc:geodeticDatum) of the geographic center of a dcterms:Location. Positive values are east of the Greenwich Meridian, negative values are west of it. Legal values lie between -180 and 180, inclusive.",
        repr=False,
        json_schema_extra={
            "$id": "http://rs.tdwg.org/dwc/terms/decimalLongitude"
        },
    )

    license: Optional[str] = Field(
        default=None,
        serialization_alias="dcterms:license",
        title="License",
        description="A legal document giving official permission to do something with the resource.",
        repr=False,
        json_schema_extra={"$id": "http://purl.org/dc/terms/license"},
    )

    owners: List[User] = Field(
        default_factory=list,
        serialization_alias="xmpRights:Owner",
        title="Copyright Owner",
        description="A list of legal owners of the resource.",
        repr=False,
        json_schema_extra={"$id": "http://ns.adobe.com/xap/1.0/rights/Owner"},
    )

    rights: Optional[str] = Field(
        default=None,
        serialization_alias="dcterms:rights",
        title="Copyright Statement",
        description="Information about rights held in and over the resource.",
        repr=False,
        json_schema_extra={"$id": "http://purl.org/dc/terms/rights"},
    )

    tags: List[Tag] = Field(
        default_factory=list,
        repr=False,
    )
    """A list of tags associated with the recording."""

    features: List[Feature] = Field(
        default_factory=list,
        repr=False,
    )
    """A list of features associated with the recording."""

    notes: List[Note] = Field(
        default_factory=list,
        repr=False,
    )
    """A list of notes associated with the recording."""

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
