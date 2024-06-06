"""Functions for recognizing audio files."""

import os
from pathlib import Path
from typing import Generator

import soundfile as sf

from soundevent.data.recordings import PathLike

__all__ = [
    "is_audio_file",
    "get_audio_files",
]


VALID_AUDIO_EXTENSIONS = {
    "aiff",
    "au",
    "avr",
    "caf",
    "flac",
    "htk",
    "ircam",
    "mat4",
    "mat5",
    "mp3",
    "mpc2k",
    "nist",
    "ogg",
    "paf",
    "pvf",
    "rf64",
    "sds",
    "svx",
    "voc",
    "w64",
    "wav",
    "wavex",
    "wve",
}


def is_audio_file(path: PathLike, strict: bool = False) -> bool:
    """Return whether the file is an audio file.

    Parameters
    ----------
    path
        Path to the file.
    strict
        Whether to check the file contents to ensure it is an audio file.
        Will take a bit longer to run, by default False.

    Returns
    -------
    bool
        Whether the file is an audio file.

    Notes
    -----
    The list of supported audio file extensions
    contains most of the audio files formats supported by the `libsndfile`
    library. See: https://libsndfile.github.io/libsndfile/

    Some formats were excluded as they do not support seeking and
    thus are not suitable for random access.

    Supported formats:

    - aiff
    - au
    - avr
    - caf
    - flac
    - htk
    - ircam
    - mat4
    - mat5
    - mp3
    - mpc2k
    - nist
    - ogg
    - paf
    - pvf
    - rf64
    - sds
    - svx
    - voc
    - w64
    - wav
    - wavex
    - wve
    """
    path = Path(path)
    if not path.is_file():
        return False

    extension = path.suffix[1:].lower()

    if extension not in VALID_AUDIO_EXTENSIONS:
        return False

    if not strict:
        return True

    try:
        sf.info(path)
    except sf.SoundFileError:
        return False

    return True


def get_audio_files(
    path: PathLike,
    strict: bool = False,
    recursive: bool = True,
    follow_symlinks: bool = False,
) -> Generator[Path, None, None]:
    """Return a generator of audio files in a directory.

    Parameters
    ----------
    path
        Path to the directory.
    strict
        Whether to check the file contents to ensure it is an audio file.
        Will take a bit longer to run, by default False.
    recursive
        Whether to search the directory recursively, by default True. This
        means that all audio files in subdirectories will be included. If
        False, only the audio files at the top level of the directory will
        be included.
    follow_symlinks
        Whether to follow symbolic links, by default False. Care should be
        taken when following symbolic links to avoid infinite loops.

    Yields
    ------
    Path
        Path to the audio file.

    Raises
    ------
    ValueError
        If the path is not a directory.

    Notes
    -----
    This function uses the
    [`is_audio_file`][soundevent.audio.files.is_audio_file] function to check
    if a file is an audio file. See the documentation for
    [`is_audio_file`][soundevent.audio.files.is_audio_file] for more
    information on which audio file formats are supported.

    Examples
    --------
    >>> from soundevent.audio.files import get_audio_files

    Get all audio files in a directory recursively:
    >>> for file in get_audio_files("path/to/directory"):
    ...     print(file)

    Get all audio files in a directory without recursion:
    >>> for file in get_audio_files(
    ...     "path/to/directory", recursive=False
    ... ):
    ...     print(file)
    """
    path = Path(path)

    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {path}")

    if not recursive:
        for file in path.iterdir():
            if is_audio_file(file, strict=strict):
                yield file
        return

    for dirpath, _, files in os.walk(path, followlinks=follow_symlinks):
        dirpath = Path(dirpath)
        for file in files:
            filepath = dirpath / file
            if is_audio_file(filepath, strict=strict):
                yield filepath
