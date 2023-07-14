"""Datasets IO module of the soundevent package.

Here you can find the classes and functions for reading and writing
Datasets of recordings.
"""

import datetime
import os
import sys
from pathlib import Path
from typing import Callable, Dict, List, Union

from soundevent import data
from soundevent.io.format import (
    DatasetInfoObject,
    DatasetObject,
    RecordingObject,
    TagObject,
    is_json,
)

if sys.version_info < (3, 6):
    from typing_extensions import Literal
else:
    from typing import Literal

if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol

__all__ = [
    "load_dataset",
    "save_dataset",
]

PathLike = Union[str, os.PathLike]


DatasetFormat = Literal["csv", "json"]


class Saver(Protocol):
    def __call__(
        self,
        dataset: data.Dataset,
        path: PathLike,
        audio_dir: PathLike = ".",
    ) -> None:
        ...


class Loader(Protocol):
    def __call__(
        self, path: PathLike, audio_dir: PathLike = "."
    ) -> data.Dataset:
        ...


Inferrer = Callable[[PathLike], bool]

SAVE_FORMATS: Dict[DatasetFormat, Saver] = {}

LOAD_FORMATS: Dict[DatasetFormat, Loader] = {}

INFER_FORMATS: Dict[DatasetFormat, Inferrer] = {
    "json": is_json,
}


def infer_format(path: PathLike) -> DatasetFormat:
    """Infer the format of a file.

    Parameters
    ----------
    path : Path
        Path to the file to infer the format of.

    Returns
    -------
    format : DatasetFormat
        The inferred format of the file.

    Raises
    ------
    ValueError
        If the format of the file cannot be inferred.

    """
    for format_, inferrer in INFER_FORMATS.items():
        if inferrer(path):
            return format_

    raise ValueError(
        f"Cannot infer format of file {path}, or format not supported."
    )


def load_dataset(path: PathLike, audio_dir: PathLike = ".") -> data.Dataset:
    """Load a Dataset from a file.

    Parameters
    ----------
    path : PathLike
        Path to the file to load.

    audio_dir : PathLike, optional
        Path to the directory containing the audio files, by default ".".
        The audio file paths in the dataset will be relative to this directory.

    Returns
    -------
    dataset : Dataset
        The loaded dataset.

    Raises
    ------
    NotImplementedError
        If the format of the file is not supported.

    """
    try:
        format_ = infer_format(path)
    except ValueError as e:
        raise NotImplementedError(f"File {path} format not supported.") from e

    loader = LOAD_FORMATS[format_]
    return loader(path, audio_dir=audio_dir)


def save_dataset(
    dataset: data.Dataset,
    path: PathLike,
    audio_dir: PathLike = ".",
    format: DatasetFormat = "json",
) -> None:
    """Save a Dataset to a file.

    Parameters
    ----------
    dataset : Dataset
        The dataset to save.
    path : Path
        Path to the file to save the dataset to.
    audio_dir : Path, optional
        Path to the directory containing the audio files, by default ".".
    format : DatasetFormat, optional
        The format to save the dataset in, by default "json".

    Raises
    ------
    NotImplementedError
        If the format of the file is not supported.

    """
    try:
        saver = SAVE_FORMATS[format]
    except KeyError as e:
        raise NotImplementedError(f"Format {format} not supported.") from e

    saver(dataset, path, audio_dir=audio_dir)


def load_dataset_json_format(
    path: PathLike,
    audio_dir: PathLike = ".",
) -> data.Dataset:
    """Load a Dataset from a JSON file.

    Parameters
    ----------
    path : Path
        Path to the file to load.

    audio_dir : Path, optional
        Path to the directory containing the audio files, by default ".".
        The audio file paths in the dataset will be relative to this directory.

    Returns
    -------
    dataset : Dataset
        The loaded dataset.
    """
    audio_dir = Path(audio_dir).resolve()

    with open(path, "r") as f:
        dataset = DatasetObject.model_validate_json(f.read())

    tags: Dict[int, data.Tag] = {}
    recordings: List[data.Recording] = []

    for tag in dataset.tags or []:
        tags[tag.id] = data.Tag(key=tag.key, value=tag.value)

    for recording in dataset.recordings:
        recording_tags = []
        for tag_id in recording.tags or []:
            recording_tags.append(tags[tag_id])

        features = []
        if recording.features:
            features = [
                data.Feature(name=name, value=value)
                for name, value in recording.features.items()
            ]

        recordings.append(
            data.Recording(
                id=recording.id,
                path=audio_dir / recording.path,
                duration=recording.duration,
                channels=recording.channels,
                samplerate=recording.samplerate,
                time_expansion=recording.time_expansion or 1.0,
                hash=recording.hash,
                date=recording.date,
                time=recording.time,
                latitude=recording.latitude,
                longitude=recording.longitude,
                tags=recording_tags,
                features=features,
                notes=recording.notes or [],
            )
        )

    return data.Dataset(
        id=dataset.info.id,
        name=dataset.info.name,
        description=dataset.info.description,
        recordings=recordings,
    )


LOAD_FORMATS["json"] = load_dataset_json_format


def save_dataset_json_format(
    dataset: data.Dataset,
    path: PathLike,
    audio_dir: PathLike = ".",
) -> None:
    """Save a Dataset to a JSON file in AOEF format.

    Parameters
    ----------
    dataset : Dataset
        The dataset to save.
    path : PathLike
        Path to the file to save the dataset to.
    audio_dir : PathLike, optional
        Path to the directory containing the audio files, by default ".".
        The audio file paths in the dataset will be relative to this directory.

    """
    audio_dir = Path(audio_dir).resolve()

    info = DatasetInfoObject(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        date_created=datetime.datetime.now(),
    )

    tags: Dict[data.Tag, TagObject] = {}
    recordings: List[RecordingObject] = []

    for recording in dataset.recordings:
        tag_ids = []
        for tag in recording.tags:
            if tag not in tags:
                tags[tag] = TagObject(
                    id=len(tags),
                    key=tag.key,
                    value=tag.value,
                )

            tag_ids.append(tags[tag].id)

        features = None
        if recording.features:
            features = {
                feature.name: feature.value for feature in recording.features
            }

        recordings.append(
            RecordingObject(
                id=recording.id,
                path=recording.path.resolve().relative_to(audio_dir),
                duration=recording.duration,
                channels=recording.channels,
                samplerate=recording.samplerate,
                time_expansion=recording.time_expansion
                if recording.time_expansion != 1.0
                else None,
                hash=recording.hash,
                date=recording.date,
                time=recording.time,
                latitude=recording.latitude,
                longitude=recording.longitude,
                tags=tag_ids if tag_ids else None,
                features=features if features else None,
                notes=recording.notes if recording.notes else None,
            )
        )

    dataset_object = DatasetObject(
        info=info,
        tags=list(tags.values()),
        recordings=recordings,
    )

    with open(path, "w") as f:
        f.write(dataset_object.model_dump_json(indent=None, exclude_none=True))


SAVE_FORMATS["json"] = save_dataset_json_format
