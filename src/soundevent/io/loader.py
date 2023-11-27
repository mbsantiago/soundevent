import sys
from typing import Dict, Optional, overload

from soundevent import data
from soundevent.io import aoef
from soundevent.io.formats import infer_format
from soundevent.io.types import DataCollections, DataType, Loader

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal  # pragma: no cover

__all__ = [
    "load",
]


@overload
def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Literal["recording_set"] = "recording_set",  # type: ignore
) -> data.RecordingSet:  # type: ignore
    ...


@overload
def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Literal["dataset"] = "dataset",  # type: ignore
) -> data.Dataset:  # type: ignore
    ...


@overload
def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Literal["annotation_set"] = "annotation_set",  # type: ignore
) -> data.AnnotationSet:  # type: ignore
    ...


@overload
def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Literal["annotation_project"] = "annotation_project",  # type: ignore
) -> data.AnnotationProject:  # type: ignore
    ...


@overload
def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Literal["prediction_set"] = "prediction_set",  # type: ignore
) -> data.PredictionSet:  # type: ignore
    ...


@overload
def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Literal["model_run"] = "model_run",  # type: ignore
) -> data.ModelRun:  # type: ignore
    ...


@overload
def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Literal["evaluation_set"] = "evaluation_set",  # type: ignore
) -> data.EvaluationSet:  # type: ignore
    ...


@overload
def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Literal["evaluation"] = "evaluation",  # type: ignore
) -> data.Evaluation:  # type: ignore
    ...


def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Optional[DataType] = None,  # type: ignore
) -> DataCollections:  # type: ignore
    """Load data from a file.

    Parameters
    ----------
    path
        Path to the file to load.
    audio_dir
        Path to the directory containing the audio files. Often, the audio
        path is stored relative to some directory to avoid storing
        absolute paths, which are not portable. In this case, the `audio_dir`
        argument is used to resolve the relative paths.
    format
        Format of the file to load. If not specified, the format is inferred.
    type
        Type of the data to load. If not specified, the type is inferred.
        This argument is mainly used for letting the type system know what
        type of object is returned by the function and can be omitted in most
        cases.
    """
    if format is None:
        format = infer_format(path)

    loader = LOADERS.get(format)
    if loader is None:
        raise ValueError(f"Unknown format {format}")

    return loader(path, audio_dir=audio_dir, type=type)


LOADERS: Dict[str, Loader] = {
    "aoef": aoef.load,
}
