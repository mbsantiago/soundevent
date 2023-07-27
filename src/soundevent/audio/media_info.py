"""Functions for getting media information from WAV files."""
import hashlib
import os
from dataclasses import dataclass
from typing import Union

from soundevent.audio.chunks import parse_into_chunks

__all__ = [
    "MediaInfo",
    "get_media_info",
    "compute_md5_checksum",
]


PathLike = Union[os.PathLike, str]


@dataclass
class MediaInfo:
    """Media information."""

    audio_format: int
    """Format code for the waveform audio data."""

    bit_depth: int
    """Bit depth."""

    samplerate_hz: int
    """Sample rate in Hz."""

    duration_s: float
    """Duration in seconds."""

    samples: int
    """Number of samples."""

    channels: int
    """Number of channels."""


def get_media_info(path: PathLike) -> MediaInfo:
    """Return the media information from the WAV file.

    The information extracted from the WAV file is the audio format,
    the bit depth, the sample rate, the duration, the number of
    samples, and the number of channels. See the documentation of
    [`MediaInfo`][soundevent.audio.MediaInfo] for more information.

    Parameters
    ----------
    path : PathLike
        Path to the WAV file.

    Returns
    -------
    [MediaInfo][soundevent.audio.MediaInfo]
        Information about the WAV file.

    Raises
    ------
    ValueError
        If the WAV file is not PCM encoded.
    """
    with open(path, "rb") as wav:
        chunk = parse_into_chunks(wav)

        # Get info from the fmt chunk. The fmt chunk is the first
        # subchunk of the root chunk.
        fmt_chunk = chunk.subchunks["fmt "]

        # Go to the start of the fmt chunk after the chunk id and
        # chunk size.
        wav.seek(fmt_chunk.position + 8)

        audio_format = int.from_bytes(wav.read(2), "little")
        channels = int.from_bytes(wav.read(2), "little")
        samplerate = int.from_bytes(wav.read(4), "little")
        wav.read(4)  # Skip byte rate.
        wav.read(2)  # Skip block align.
        bit_depth = int.from_bytes(wav.read(2), "little")

        # Get size of data chunk. Notice that the size of the data
        # chunk is the size of the data subchunk divided by the number
        # of channels and the bit depth.
        data_chunk = chunk.subchunks["data"]
        samples = 8 * data_chunk.size // (channels * bit_depth)

        duration = samples / samplerate

    return MediaInfo(
        audio_format=audio_format,
        bit_depth=audio_format,
        samplerate_hz=samplerate,
        channels=channels,
        samples=samples,
        duration_s=duration,
    )


BUFFER_SIZE = 65536


def compute_md5_checksum(path: PathLike) -> str:
    """Compute the MD5 checksum of a file.

    Parameters
    ----------
    path : PathLike
        Path to the file.

    Returns
    -------
    str
        MD5 checksum of the file.
    """
    md5 = hashlib.md5()
    with open(path, "rb") as fp:
        buffer = fp.read(BUFFER_SIZE)
        while len(buffer) > 0:
            md5.update(buffer)
            buffer = fp.read(BUFFER_SIZE)
    return md5.hexdigest()
