"""Functions for getting media information from WAV files."""
import hashlib
import os
from dataclasses import dataclass
from typing import IO, Union

from soundevent.audio.chunks import Chunk, parse_into_chunks

__all__ = [
    "MediaInfo",
    "get_media_info",
    "compute_md5_checksum",
]


PathLike = Union[os.PathLike, str]


@dataclass
class FormatInfo:
    """Information stored in the format chunk."""

    audio_format: int
    """Format code for the waveform audio data."""

    bit_depth: int
    """Bit depth."""

    samplerate: int
    """Sample rate in Hz."""

    channels: int
    """Number of channels."""

    byte_rate: int
    """Byte rate.

    byte_rate = samplerate * channels * bit_depth/8
    """

    block_align: int
    """Block align.

    The number of bytes for one sample including all channels.
    block_align = channels * bit_depth/8
    """


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


def extract_media_info_from_chunks(
    fp: IO[bytes],
    fmt_chunk: Chunk,
) -> FormatInfo:
    """Return the media information from the fmt chunk.

    Parameters
    ----------
    fp : BytesIO
        File pointer to the WAV file.

    chunk : Chunk
        The fmt chunk.

    Returns
    -------
    MediaInfo

    Notes
    -----
    The structure of the format chunk is described in
    (WAV PCM soundfile format)[http://soundfile.sapp.org/doc/WaveFormat/].
    """
    # Go to the start of the fmt chunk after the chunk id and
    # chunk size.
    fp.seek(fmt_chunk.position + 8)

    audio_format = int.from_bytes(fp.read(2), "little")
    channels = int.from_bytes(fp.read(2), "little")
    samplerate = int.from_bytes(fp.read(4), "little")
    byte_rate = int.from_bytes(fp.read(4), "little")
    block_align = int.from_bytes(fp.read(2), "little")
    bit_depth = int.from_bytes(fp.read(2), "little")

    return FormatInfo(
        audio_format=audio_format,
        bit_depth=bit_depth,
        samplerate=samplerate,
        channels=channels,
        byte_rate=byte_rate,
        block_align=block_align,
    )


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

        # Get info from the fmt chunk
        fmt = chunk.subchunks["fmt "]
        fmt_info = extract_media_info_from_chunks(wav, fmt)

        # Get size of data chunk. Notice that the size of the data
        # chunk is the size of the data subchunk divided by the number
        # of channels and the bit depth.
        data_chunk = chunk.subchunks["data"]
        samples = (
            8 * data_chunk.size // (fmt_info.channels * fmt_info.bit_depth)
        )
        duration = samples / fmt_info.samplerate

        return MediaInfo(
            audio_format=fmt_info.audio_format,
            bit_depth=fmt_info.bit_depth,
            samplerate_hz=fmt_info.samplerate,
            duration_s=duration,
            samples=samples,
            channels=fmt_info.channels,
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
