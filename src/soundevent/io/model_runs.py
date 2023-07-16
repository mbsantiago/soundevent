"""Model Runs IO module of the soundevent package.

Here you can find the classes and functions for reading and writing model runs.
"""

from pathlib import Path
from typing import Dict, Optional

from soundevent import data
from soundevent.io.formats import aoef, infer_format
from soundevent.io.types import Loader, PathLike, Saver

__all__ = [
    "load_model_run",
    "save_model_run",
]


SAVE_FORMATS: Dict[str, Saver[data.ModelRun]] = {}
LOAD_FORMATS: Dict[str, Loader[data.ModelRun]] = {}


def load_model_run(
    path: PathLike, audio_dir: Optional[PathLike] = None
) -> data.ModelRun:
    """Load a ModelRun from a file.

    Parameters
    ----------
    path : PathLike
        Path to the file to load.

    audio_dir : PathLike, optional
        Path to the directory containing the audio files. If provided, the
        audio file paths in the model run will be relative to this directory.

    Returns
    -------
    model_run : ModelRun
        The loaded model run.

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


def save_model_run(
    model_run: data.ModelRun,
    path: PathLike,
    audio_dir: Optional[PathLike] = None,
    format: str = "aoef",
) -> None:
    """Save a ModelRun to a file.

    Parameters
    ----------
    model_run : ModelRun
        The model run to save.

    path : Path
        Path to the file to save the dataset to.

    audio_dir : Path, optional
        Path to the directory containing the audio files. If provided, the
        audio file paths in the model run will be relative to this directory.
        Defaults to None.

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

    saver(model_run, path, audio_dir=audio_dir)


def load_model_run_aoef_format(
    path: PathLike,
    audio_dir: Optional[PathLike] = None,
) -> data.ModelRun:
    """Load a ModelRun from a JSON file in AOEF format.

    Parameters
    ----------
    path : Path
        Path to the file to load.

    audio_dir : Path, optional
        Path to the directory containing the audio files. If provided, the
        audio file paths in the model run will be relative to this directory.
        Defaults to None.

    Returns
    -------
    model_run : ModelRun
        The loaded model run.
    """
    if audio_dir is not None:
        audio_dir = Path(audio_dir).resolve()

    with open(path, "r") as f:
        dataset = aoef.ModelRunObject.model_validate_json(f.read())

    return dataset.to_model_run(audio_dir=audio_dir)


def save_model_run_aoef_format(
    obj: data.ModelRun,
    path: PathLike,
    audio_dir: Optional[PathLike] = None,
) -> None:
    """Save a ModelRun to a JSON file in AOEF format.

    Parameters
    ----------
    obj : ModelRun
        The model run to save.

    path : PathLike
        Path to the file to save the dataset to.

    audio_dir : PathLike, optional
        Path to the directory containing the audio files. If provided, the
        audio file paths in the model run will be relative to this directory.
        Defaults to None.

    """
    if audio_dir is not None:
        audio_dir = Path(audio_dir).resolve()

    dataset_object = aoef.ModelRunObject.from_model_run(
        obj,
        audio_dir=audio_dir,
    )

    with open(path, "w") as f:
        f.write(dataset_object.model_dump_json(indent=None, exclude_none=True))


SAVE_FORMATS["aoef"] = save_model_run_aoef_format
LOAD_FORMATS["aoef"] = load_model_run_aoef_format
