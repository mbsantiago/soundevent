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
from pathlib import Path
from typing import Any, Dict, Optional, Set, TypeVar, Union

from pydantic import BaseModel, Field

from .annotation_project import (
    AnnotationProjectAdapter,
    AnnotationProjectObject,
)
from .annotation_set import AnnotationSetAdapter, AnnotationSetObject
from .dataset import DatasetAdapter, DatasetObject
from .evaluation import EvaluationAdapter, EvaluationObject
from .evaluation_set import EvaluationSetAdapter, EvaluationSetObject
from .model_run import ModelRunAdapter, ModelRunObject
from .prediction_set import PredictionSetAdapter, PredictionSetObject
from .recording_set import RecordingSetAdapter, RecordingSetObject
from soundevent import data
from soundevent.io.types import DataCollections, DataType
from soundevent.io.utils import is_json

__all__ = [
    "load",
    "save",
    "to_aeof",
    "to_soundevent",
    "RecordingSetObject",
    "DatasetObject",
    "AnnotationSetObject",
    "AnnotationProjectObject",
    "EvaluationObject",
    "EvaluationSetObject",
    "PredictionSetObject",
    "ModelRunObject",
]

C = TypeVar("C", bound=BaseModel)
D = TypeVar("D", bound=BaseModel)

AOEF_VERSION = "1.1.0"

# NOTE: The order of the adapters is important, as the first matching adapter
# will be used to convert the data object. Since the `data` module uses
# inheritance, we need to make sure that the more specific adapters are listed
# first.
ADAPTERS = [
    ("evaluation", data.Evaluation, EvaluationAdapter),
    ("dataset", data.Dataset, DatasetAdapter),
    ("annotation_project", data.AnnotationProject, AnnotationProjectAdapter),
    ("evaluation_set", data.EvaluationSet, EvaluationSetAdapter),
    ("model_run", data.ModelRun, ModelRunAdapter),
    ("annotation_set", data.AnnotationSet, AnnotationSetAdapter),
    ("prediction_set", data.PredictionSet, PredictionSetAdapter),
    ("recording_set", data.RecordingSet, RecordingSetAdapter),
]


class AOEFObject(BaseModel):
    """Schema definition for an AOEF object."""

    version: str = AOEF_VERSION
    created_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )
    data: Union[
        EvaluationObject,
        DatasetObject,
        AnnotationProjectObject,
        EvaluationSetObject,
        ModelRunObject,
        AnnotationSetObject,
        PredictionSetObject,
        RecordingSetObject,
    ] = Field(discriminator="collection_type")


def to_aeof(
    obj: DataCollections,
    audio_dir: Optional[data.PathLike] = None,
) -> AOEFObject:
    """Convert a data object to an AOEF object."""
    for _, data_cls, adapter_cls in ADAPTERS:
        if isinstance(obj, data_cls):
            adapter = adapter_cls(audio_dir=audio_dir)
            return AOEFObject(
                data=adapter.to_aoef(obj),
                created_on=datetime.datetime.now(),
            )

    raise NotImplementedError(f"Unsupported data type: {type(obj)}")


def to_soundevent(
    aoef_object: AOEFObject,
    audio_dir: Optional[data.PathLike] = None,
) -> DataCollections:
    """Convert an AOEF object to a data object."""
    for adapter_type, _, adapter_cls in ADAPTERS:
        if aoef_object.data.collection_type == adapter_type:
            adapter = adapter_cls(audio_dir=audio_dir)
            return adapter.to_soundevent(aoef_object.data)  # type: ignore

    raise NotImplementedError(
        f"Unsupported data type: {aoef_object.data.collection_type}"
    )


def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    type: Optional[DataType] = None,
) -> DataCollections:
    """Load an AOEF object from a JSON file."""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not is_json(path):
        raise ValueError(f"Invalid file type: {path.suffix}")

    aoef_object = AOEFObject.model_validate_json(path.read_text())

    if type is not None and aoef_object.data.collection_type != type:
        raise ValueError(
            f"Invalid data type: {aoef_object.data.collection_type} (expected {type})"
        )

    if aoef_object.version != AOEF_VERSION:
        version = aoef_object.version
        raise ValueError(
            f"Invalid AOEF version: {version} (expected {AOEF_VERSION})"
        )

    return to_soundevent(aoef_object, audio_dir=audio_dir)


IncEx = Union[Set[int], Set[str], Dict[int, Any], Dict[str, Any], None]


def save(
    obj: DataCollections,
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    exclude: IncEx = None,
) -> None:
    """Save an AOEF object to a JSON file."""
    path = Path(path)

    if not path.parent.exists():
        path.parent.mkdir(parents=True)

    aoef_object = to_aeof(obj, audio_dir=audio_dir)

    path.write_text(
        aoef_object.model_dump_json(
            exclude_none=True,
            exclude=exclude,
        )
    )
