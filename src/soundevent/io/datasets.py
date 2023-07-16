"""Datasets IO module of the soundevent package.

Here you can find the classes and functions for reading and writing
Datasets of recordings.
"""

from pathlib import Path
from typing import Dict, Optional

from soundevent import data
from soundevent.io.formats import aoef, infer_format
from soundevent.io.types import Loader, PathLike, Saver

__all__ = [
    "load_dataset",
    "save_dataset",
]


SAVE_FORMATS: Dict[str, Saver[data.Dataset]] = {}
LOAD_FORMATS: Dict[str, Loader[data.Dataset]] = {}


def load_dataset(
    path: PathLike,
    audio_dir: Optional[PathLike] = None,
) -> data.Dataset:
    """Load a Dataset from a file.

    Parameters
    ----------
    path : PathLike
        Path to the file to load.

    audio_dir : PathLike, optional
        Path to the directory containing the audio files. If provided, the
        audio file paths in the dataset will be relative to this directory.
        By default None.

    Returns
    -------
    dataset : Dataset
        The loaded dataset.

    Raises
    ------
    NotImplementedError
        If the format of the file is not supported.

    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Path {path} does not exist.")

    try:
        format_ = infer_format(path)
    except ValueError as e:
        raise NotImplementedError(f"File {path} format not supported.") from e

    loader = LOAD_FORMATS[format_]
    return loader(path, audio_dir=audio_dir)


def save_dataset(
    dataset: data.Dataset,
    path: PathLike,
    audio_dir: Optional[PathLike] = None,
    format: str = "aoef",
) -> None:
    """Save a Dataset to a file.

    Parameters
    ----------
    dataset : Dataset
        The dataset to save.

    path : Path
        Path to the file to save the dataset to.

    audio_dir : Path, optional
        Path to the directory containing the audio files. If provided, the
        audio file paths in the dataset will be relative to this directory.
        By default None.

    format : DatasetFormat, optional
        The format to save the dataset in, by default "aoef".

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


def load_dataset_aoef_format(
    path: PathLike,
    audio_dir: Optional[PathLike] = None,
) -> data.Dataset:
    """Load a Dataset from a JSON file.

    Parameters
    ----------
    path : Path
        Path to the file to load.

    audio_dir : Path, optional
        Path to the directory containing the audio files. If provided, the
        audio file paths in the dataset will be relative to this directory.
        By default None.

    Returns
    -------
    dataset : Dataset
        The loaded dataset.
    """
    if audio_dir is not None:
        audio_dir = Path(audio_dir).resolve()

    with open(path, "r") as f:
        dataset = aoef.DatasetObject.model_validate_json(f.read())

    return dataset.to_dataset(audio_dir=audio_dir)


def save_dataset_aoef_format(
    obj: data.Dataset,
    path: PathLike,
    audio_dir: Optional[PathLike] = None,
) -> None:
    """Save a Dataset to a JSON file in AOEF format.

    Parameters
    ----------
    dataset : Dataset
        The dataset to save.
    path : PathLike
        Path to the file to save the dataset to.
    audio_dir : PathLike, optional
        Path to the directory containing the audio files. If provided, the
        audio file paths in the dataset will be relative to this directory.
        By default None.

    """
    if audio_dir is not None:
        audio_dir = Path(audio_dir).resolve()

    dataset_object = aoef.DatasetObject.from_dataset(
        obj,
        audio_dir=audio_dir,
    )

    with open(path, "w") as f:
        f.write(dataset_object.model_dump_json(indent=None, exclude_none=True))


SAVE_FORMATS["aoef"] = save_dataset_aoef_format
LOAD_FORMATS["aoef"] = load_dataset_aoef_format
