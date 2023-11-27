"""Submodule of io module containing type definitions."""
import sys
from typing import Generic, Optional, TypeVar, Union

from soundevent import data

if sys.version_info < (3, 8):
    from typing_extensions import Literal, Protocol  # pragma: no cover
else:
    from typing import Literal, Protocol

__all__ = [
    "Saver",
    "Loader",
]


T = TypeVar("T", covariant=True)


DataType = Literal[
    "dataset",
    "annotation_set",
    "annotation_project",
    "prediction_set",
    "model_run",
    "evaluation_set",
    "evaluation",
    "recording_set",
]

DataCollections = Union[
    data.Dataset,
    data.AnnotationSet,
    data.AnnotationProject,
    data.PredictionSet,
    data.ModelRun,
    data.EvaluationSet,
    data.Evaluation,
    data.RecordingSet,
]
"""Type alias for all data collection types."""

D = TypeVar("D", contravariant=True, bound=DataCollections)


class Saver(Protocol, Generic[D]):
    """Protocol for saving functions."""

    def __call__(
        self,
        obj: D,
        path: data.PathLike,
        audio_dir: Optional[data.PathLike] = None,
    ) -> None:
        """Save object to path."""
        ...  # pragma: no cover


class Loader(Protocol, Generic[T]):
    """Protocol for loading functions."""

    def __call__(
        self,
        path: data.PathLike,
        audio_dir: Optional[data.PathLike] = None,
        type: Optional[DataType] = None,
    ) -> T:
        """Load object from path."""
        ...  # pragma: no cover
