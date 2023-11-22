import sys
from typing import Dict, Optional, overload

from soundevent import data
from soundevent.io import aoef
from soundevent.io.formats import infer_format
from soundevent.io.types import DataObject, DataType, Loader

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


@overload
def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Literal["dataset"] = "dataset",
) -> data.Dataset:
    ...


@overload
def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Literal["annotation_set"] = "annotation_set",
) -> data.AnnotationSet:
    ...


@overload
def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Literal["annotation_project"] = "annotation_project",
) -> data.AnnotationProject:
    ...


@overload
def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Literal["prediction_set"] = "prediction_set",
) -> data.PredictionSet:
    ...


@overload
def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Literal["model_run"] = "model_run",
) -> data.ModelRun:
    ...


@overload
def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Literal["evaluation_set"] = "evaluation_set",
) -> data.EvaluationSet:
    ...


@overload
def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Literal["evaluation"] = "evaluation",
) -> data.Evaluation:
    ...


def load(
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: Optional[str] = "aoef",
    type: Optional[DataType] = None,
) -> DataObject:
    if format is None:
        format = infer_format(path)

    loader = LOADERS.get(format)
    if loader is None:
        raise ValueError(f"Unknown format {format}")

    return loader(path, audio_dir=audio_dir, type=type)


LOADERS: Dict[str, Loader] = {
    "aoef": aoef.load,
}
