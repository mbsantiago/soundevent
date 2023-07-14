"""Acoustic Objects Exchange Format (AOEF) - Data Storage Schema.

The `soundevent.io.format` module provides the schema definition for the
Acoustic Objects Exchange Format (AOEF), a JSON-based format designed to
facilitate the storage and exchange of acoustic data objects. Inspired by the
Common Objects in Context (COCO) format, AOEF offers a standardized and easily
shareable format for researchers working with bioacoustic data.

By utilizing AOEF, researchers can ensure consistency and interoperability when
storing and exchanging acoustic objects. The format leverages Pydantic data
objects for validation, ensuring data integrity and adherence to the defined
schema.

## Benefits of AOEF

* Standardization: AOEF defines a consistent structure for representing acoustic
data objects, enabling seamless sharing and collaboration among researchers.

* Ease of Exchange: The JSON-based format makes it simple to share and exchange
data objects across different platforms and systems.

* Validation and Data Integrity: The schema validation provided by Pydantic
ensures that the data objects conform to the specified structure, reducing the
risk of errors and inconsistencies.

"""
import datetime
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from soundevent import data

__all__ = [
    "TagObject",
    "RecordingObject",
    "DatasetInfoObject",
    "DatasetObject",
    "is_json",
]


class TagObject(BaseModel):
    """Schema definition for a tag object in AOEF format."""

    id: int

    key: str

    value: str


class RecordingObject(BaseModel):
    """Schema definition for a recording object in AOEF format."""

    id: UUID

    path: Path

    duration: float

    channels: int

    samplerate: int

    time_expansion: Optional[float] = None

    hash: Optional[str] = None

    date: Optional[datetime.date] = None

    time: Optional[datetime.time] = None

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    tags: Optional[List[int]] = None

    features: Optional[Dict[str, float]] = None

    notes: Optional[List[data.Note]] = None


class DatasetInfoObject(BaseModel):
    """Schema definition for a dataset info object in AOEF format."""

    id: UUID
    """The unique identifier of the dataset."""

    name: str
    """The name of the dataset."""

    description: Optional[str] = None
    """A description of the dataset."""

    date_created: datetime.datetime
    """The date and time at which the file dataset was created."""


class DatasetObject(BaseModel):
    """Schema definition for a dataset object in AOEF format."""

    info: DatasetInfoObject

    tags: Optional[List[TagObject]] = None

    recordings: List[RecordingObject]


def is_json(path: Union[str, os.PathLike]) -> bool:
    """Check if a file is a JSON file."""
    path = Path(path)
    return path.suffix == ".json"
