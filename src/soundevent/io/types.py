"""Submodule of io module containing type definitions."""
import sys
from typing import Generic, Optional, TypeVar

from soundevent.data.recordings import PathLike

if sys.version_info < (3, 8):
    from typing_extensions import Protocol  # pragma: no cover
else:
    from typing import Protocol

__all__ = [
    "PathLike",
    "Saver",
    "Loader",
]


D = TypeVar("D", contravariant=True)
T = TypeVar("T", covariant=True)


class Saver(Protocol, Generic[D]):
    """Protocol for saving functions."""

    def __call__(
        self,
        obj: D,
        path: PathLike,
        audio_dir: Optional[PathLike] = None,
    ) -> None:
        """Save object to path."""
        ...  # pragma: no cover


class Loader(Protocol, Generic[T]):
    """Protocol for loading functions."""

    def __call__(
        self,
        path: PathLike,
        audio_dir: Optional[PathLike] = None,
    ) -> T:
        """Load object from path."""
        ...  # pragma: no cover
