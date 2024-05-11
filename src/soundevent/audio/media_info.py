"""Functions for getting media information from WAV files."""

import hashlib
import struct
from dataclasses import dataclass

import soundfile as sf

from soundevent.data.recordings import PathLike

__all__ = [
    "MediaInfo",
    "get_media_info",
    "compute_md5_checksum",
    "compute_sha2_checksum",
]


@dataclass
class MediaInfo:
    """MediaInfo Class.

    Encapsulates essential metadata about audio data for processing and
    analysis. The information stored in this dataclass can typically be
    automatically extracted from the audio file itself.
    """

    samplerate_hz: int
    """The sampling rate of the audio, measured in Hertz (Hz). 

    This indicates the number of samples taken per second to represent the
    analog audio signal.
    """

    duration_s: float
    """The total duration of the audio, measured in seconds (s).

    This represents the length of time the audio recording spans.
    """

    samples: int
    """The total number of samples in the audio data."""

    channels: int
    """The number of audio channels present in the data.

    For example 1 for mono, 2 for stereo."""

    format: str
    """A code representing the audio file format. 

    For example "WAV", "MP3".
    """

    subtype: str
    """A more specific subtype of the audio format. 

    For example "PCM_16", "A_LAW". These subtypes provide additional
    information about the audio data, such as the bit depth for PCM encoded
    audio, or encoding algorithm for compressed audio formats.
    """


def get_media_info(path: PathLike) -> MediaInfo:
    """Return the media information from the WAV file.

    The information extracted from the WAV file is the audio format,
    the bit depth, the sample rate, the duration, the number of
    samples, and the number of channels.

    Parameters
    ----------
    path
        Path to the WAV file.

    Returns
    -------
    media_info: MediaInfo
        Information about the WAV file.

    Raises
    ------
    ValueError
        If the WAV file is not PCM encoded.
    """
    info = sf.info(path)
    return MediaInfo(
        samplerate_hz=info.samplerate,
        duration_s=info.duration,
        samples=info.frames,
        channels=info.channels,
        format=info.format,
        subtype=info.subtype,
    )


BUFFER_SIZE = 65536


def compute_md5_checksum(path: PathLike) -> str:
    """Compute the MD5 checksum of a file.

    Parameters
    ----------
    path
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


def compute_sha2_checksum(path: PathLike) -> str:
    """Compute the SHA-256 checksum of a file.

    Parameters
    ----------
    path
        Path to the file.

    Returns
    -------
    str
        SHA-256 checksum of the file.
    """
    sha2 = hashlib.sha256()
    with open(path, "rb") as fp:
        buffer = fp.read(BUFFER_SIZE)
        while len(buffer) > 0:
            sha2.update(buffer)
            buffer = fp.read(BUFFER_SIZE)
    return sha2.hexdigest()


def generate_wav_header(
    samplerate: int,
    channels: int,
    samples: int,
    bit_depth: int = 16,
) -> bytes:
    """Generate the data of a WAV header.

    This function generates the data of a WAV header according to the
    given parameters. The WAV header is a 44-byte string that contains
    information about the audio data, such as the sample rate, the
    number of channels, and the number of samples. The WAV header
    assumes that the audio data is PCM encoded.

    Parameters
    ----------
    samplerate
        Sample rate in Hz.
    channels
        Number of channels.
    samples
        Number of samples.
    bit_depth
        The number of bits per sample. By default, it is 16 bits.

    Notes
    -----
    The structure of the WAV header is described in
    (WAV PCM soundfile format)[http://soundfile.sapp.org/doc/WaveFormat/].
    """
    data_size = samples * channels * bit_depth // 8
    byte_rate = samplerate * channels * bit_depth // 8
    block_align = channels * bit_depth // 8

    return struct.pack(
        "<4si4s4sihhiihh4si",  # Format string
        b"RIFF",  # RIFF chunk id
        data_size + 36,  # Size of the entire file minus 8 bytes
        b"WAVE",  # RIFF chunk id
        b"fmt ",  # fmt chunk id
        16,  # Size of the fmt chunk
        1,  # Audio format (1 corresponds to PCM)
        channels,  # Number of channels
        samplerate,  # Sample rate in Hz
        byte_rate,  # Byte rate
        block_align,  # Block align
        bit_depth,  # Number of bits per sample
        b"data",  # data chunk id
        data_size,  # Size of the data chunk
    )
