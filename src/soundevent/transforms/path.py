from collections.abc import Callable
from pathlib import Path

from soundevent import data
from soundevent.transforms.base import TransformBase

__all__ = [
    "PathTransform",
]


class PathTransform(TransformBase):
    def __init__(self, transform: Callable[[Path], Path]):
        self.transform = transform

    def transform_recording(self, recording: data.Recording) -> data.Recording:
        return recording.model_copy(
            update=dict(path=self.transform(recording.path))
        )
