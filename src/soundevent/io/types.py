"""Submodule of io module containing type definitions."""

from typing import Generic, Literal, Protocol, TypeVar

from soundevent import data

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

DataCollections = (
    data.Dataset
    | data.AnnotationSet
    | data.AnnotationProject
    | data.PredictionSet
    | data.ModelRun
    | data.EvaluationSet
    | data.Evaluation
    | data.RecordingSet
)
"""Type alias for all data collection types."""

D = TypeVar("D", contravariant=True, bound=DataCollections)


class Saver(Protocol, Generic[D]):
    """Protocol for saving functions."""

    def __call__(
        self,
        obj: D,
        path: data.PathLike,
        audio_dir: data.PathLike | None = None,
    ) -> None:
        """Save object to path."""
        ...  # pragma: no cover


class Loader(Protocol, Generic[T]):
    """Protocol for loading functions."""

    def __call__(
        self,
        path: data.PathLike,
        audio_dir: data.PathLike | None = None,
        type: DataType | None = None,
    ) -> T:
        """Load object from path."""
        ...  # pragma: no cover
