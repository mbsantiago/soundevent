"""Datasets."""

from pathlib import Path
from typing import Optional

from soundevent.data.recording_sets import RecordingSet
from soundevent.data.recordings import PathLike, Recording

__all__ = ["Dataset"]


class Dataset(RecordingSet):
    name: str

    description: Optional[str] = None

    @classmethod
    def from_directory(
        cls,
        path: PathLike,
        name: str,
        description: Optional[str] = None,
        recursive: bool = True,
        compute_hash: bool = True,
    ) -> "Dataset":
        """Return a dataset from the directory.

        Reads the audio files in the directory and returns a dataset
        containing the recordings.

        Parameters
        ----------
        path : PathLike
            Path to the directory.
        recursive : bool, optional
            Whether to search the directory recursively, by default True
        compute_hash : bool, optional
            Whether to compute the hash of the audio files, by default

        Returns
        -------
        Dataset
            The dataset.

        Raises
        ------
        ValueError
            If the path is not a directory.
        """
        path = Path(path)

        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        glob_pattern = "**/*.wav" if recursive else "*.wav"

        recordings = [
            Recording.from_file(file, compute_hash=compute_hash)
            for file in path.glob(glob_pattern)
        ]

        return cls(
            name=name,
            description=description,
            recordings=recordings,
        )
