"""Transformations for recording paths."""

from collections.abc import Callable
from pathlib import Path

from soundevent.transforms.base import TransformBase

__all__ = [
    "PathTransform",
]


class PathTransform(TransformBase):
    """A transform for modifying the path of recordings.

    This class provides a convenient way to apply a path transformation
    to all `Recording` objects within a larger data structure (like a
    `Dataset` or `AnnotationProject`). It works by overriding the
    `transform_path` method of the `TransformBase`.

    Parameters
    ----------
    transform : Callable[[Path], Path]
        A function that takes a `pathlib.Path` object and returns a
        transformed `pathlib.Path` object.

    Examples
    --------
    >>> from pathlib import Path
    >>> from soundevent import data
    >>> from soundevent.transforms import PathTransform
    >>>
    >>> # Create a sample dataset to work with
    >>> recording = data.Recording(
    ...     path=Path("../relative/path/rec.wav"),
    ...     duration=1,
    ...     channels=1,
    ...     samplerate=16000,
    ... )
    >>> dataset = data.Dataset(name="test-dataset", recordings=[recording])
    >>>
    >>> # Define a function to make all paths absolute
    >>> def make_absolute(path: Path) -> Path:
    ...     # This is a simplistic example, in reality you might need a base directory
    ...     return path.resolve()
    >>>
    >>> # Create and apply the transform
    >>> path_transformer = PathTransform(transform=make_absolute)
    >>> transformed_dataset = path_transformer.transform_dataset(dataset)
    >>>
    >>> # Check that the path in the transformed dataset is absolute
    >>> transformed_dataset.recordings[0].path.is_absolute()
    True

    """

    def __init__(self, transform: Callable[[Path], Path]):
        """Initialize the PathTransform.

        Parameters
        ----------
        transform : Callable[[Path], Path]
            A function that takes a `pathlib.Path` object and returns a
            transformed `pathlib.Path` object.
        """
        self.transform = transform

    def transform_path(self, path: Path) -> Path:
        """Apply the transformation to a path.

        Parameters
        ----------
        path : Path
            The path to transform.

        Returns
        -------
        Path
            The transformed path.
        """
        return self.transform(path)
