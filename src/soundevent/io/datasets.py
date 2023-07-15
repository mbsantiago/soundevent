"""Datasets IO module of the soundevent package.

Here you can find the classes and functions for reading and writing
Datasets of recordings.
"""

import os
import sys
from pathlib import Path
from typing import Callable, Dict, Union

from soundevent import data
from soundevent.io.format import DatasetObject, is_json

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

    return dataset.to_dataset(audio_dir=audio_dir)


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

    dataset_object = DatasetObject.from_dataset(
        dataset,
        audio_dir=audio_dir,
    )

    with open(path, "w") as f:
        f.write(dataset_object.model_dump_json(indent=None, exclude_none=True))


SAVE_FORMATS["json"] = save_dataset_json_format
