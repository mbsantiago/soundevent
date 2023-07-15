"""Submodule of io module containing type definitions."""
import os
import sys
from typing import Generic, TypeVar, Union

if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol

__all__ = [
    "PathLike",
    "Saver",
    "Loader",
]

PathLike = Union[str, os.PathLike]


D = TypeVar("D", contravariant=True)
T = TypeVar("T", covariant=True)


class Saver(Protocol, Generic[D]):
    """Protocol for saving functions."""

    def __call__(
        self,
        obj: D,
        path: PathLike,
        audio_dir: PathLike = ".",
    ) -> None:
        """Save object to path."""
        ...


class Loader(Protocol, Generic[T]):
    """Protocol for loading functions."""

    def __call__(self, path: PathLike, audio_dir: PathLike = ".") -> T:
        """Load object from path."""
        ...
