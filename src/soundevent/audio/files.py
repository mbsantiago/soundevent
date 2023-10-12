"""Functions for recognizing audio files.

For now only WAV files are supported.
"""

from pathlib import Path

from soundevent.data.recordings import PathLike

__all__ = [
    "is_audio_file",
]


def is_audio_file(path: PathLike) -> bool:
    """Return whether the file is an audio file.

    Parameters
    ----------
    path
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
