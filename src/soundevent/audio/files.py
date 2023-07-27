"""Functions for recognizing audio files.

For now only WAV files are supported.
"""


import os
from pathlib import Path
from typing import Union

__all__ = [
    "is_audio_file",
]

PathLike = Union[os.PathLike, str]


def is_audio_file(path: PathLike) -> bool:
    """Return whether the file is an audio file.

    Parameters
    ----------
    path : PathLike
        Path to the file.

    Returns
    -------
    bool
        Whether the file is an audio file.
    """
    path = Path(path)
    if not path.is_file():
        return False
    return path.suffix.lower() in (".wav",)
