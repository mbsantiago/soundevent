"""Input and output functions for soundevent.

Currently only supports reading and writing of .wav files.
"""
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import soundfile as sf
import xarray as xr

from soundevent import data
from soundevent.audio.chunks import parse_into_chunks
from soundevent.audio.media_info import extract_media_info_from_chunks
from soundevent.audio.raw import RawData

__all__ = [
    "load_audio",
    "load_recording",
    "load_clip",
]

PCM_SUBFORMATS_MAPPING: Dict[Tuple[int, int], str] = {
    (1, 16): "PCM_16",
    (1, 24): "PCM_24",
    (1, 32): "PCM_32",
    (1, 8): "PCM_U8",
    (3, 32): "FLOAT",
    (3, 64): "DOUBLE",
    (6, 8): "ALAW",
    (7, 8): "ULAW",
}


def load_audio(
    path: data.PathLike,
    offset: int = 0,
    samples: Optional[int] = None,
) -> Tuple[np.ndarray, int]:
    """Load an audio file.

    Parameters
    ----------
    path
        The path to the audio file.
    offset
        The offset in samples from the start of the audio file.
    samples
        The number of samples to load. If None, load the entire file.

    Returns
    -------
    np.ndarray
        The audio data.
    samplerate : int
        The sample rate of the audio file in Hz.
    """
    if samples is None:
        samples = -1

    with open(path, "rb") as fp:
        chunks = parse_into_chunks(fp)

        # Extract the media information from the fmt chunk.
        fmt = chunks.subchunks["fmt "]
        media_info = extract_media_info_from_chunks(fp, fmt)

        # Get the subformat for the soundfile library to
        # read the audio data.
        subformat = PCM_SUBFORMATS_MAPPING.get(
            (media_info.audio_format, media_info.bit_depth)
        )
        if subformat is None:
            raise ValueError(
                f"Unsupported audio format: {media_info.audio_format} "
                f"with bit depth {media_info.bit_depth}."
                "Valid formats are: "
                f"{PCM_SUBFORMATS_MAPPING.keys()}."
            )

        # Position the file pointer at the start of the data chunk.
        data = chunks.subchunks["data"]
        raw = RawData(fp, data)

        return sf.read(
            raw,
            start=offset,
            frames=samples,
            dtype="float32",
            always_2d=True,
            format="RAW",
            subtype=subformat,
            samplerate=media_info.samplerate,
            channels=media_info.channels,
            fill_value=0,
        )


def load_recording(
    recording: data.Recording,
    audio_dir: Optional[data.PathLike] = None,
) -> xr.DataArray:
    """Load a recording from a file.

    Parameters
    ----------
    recording
        The recording to load.
    audio_dir
        The directory containing the audio file. If None, the
        recording path is assumed to be relative to the current
        working directory or an absolute path.

    Returns
    -------
    audio : xr.DataArray
        The loaded recording.
    """
    path = recording.path

    if audio_dir is not None:
        path = Path(audio_dir) / path

    data, _ = load_audio(path)
    return xr.DataArray(
        data=data,
        dims=("time", "channel"),
        coords={
            "time": np.linspace(
                0,
                recording.duration,
                data.shape[0],
                endpoint=False,
            ),
            "channel": range(data.shape[1]),
        },
        attrs={
            "recording_id": recording.uuid,
            "path": recording.path,
            "time_units": "seconds",
            "time_expansion": recording.time_expansion,
            "samplerate": recording.samplerate,
        },
    )


def load_clip(
    clip: data.Clip,
    audio_dir: Optional[data.PathLike] = None,
) -> xr.DataArray:
    """Load a clip from a file.

    Parameters
    ----------
    clip
        The clip to load.
    audio_dir
        The directory containing the audio file. If None, the
        recording path is assumed to be relative to the current
        working directory or an absolute path.

    Returns
    -------
    audio : xr.DataArray
        The loaded clip. The returned clip stores the samplerate
        and time expansion of the recording from which it was
        extracted.
    """
    recording = clip.recording
    samplerate = recording.samplerate

    offset = int(np.floor(clip.start_time * samplerate))
    duration = clip.end_time - clip.start_time
    samples = int(np.ceil(duration * samplerate))

    path = recording.path
    if audio_dir is not None:
        path = Path(audio_dir) / path

    data, _ = load_audio(
        path,
        offset=offset,
        samples=samples,
    )

    # Adjust start and end time to be on sample boundaries. This is necessary
    # because the specified start and end time might not align precisely with
    # the sampling moments of the audio. By aligning with the sample
    # boundaries, we ensure that any time location within the clip, relative to
    # the original audio file, remains accurate.
    start_time = offset / samplerate
    end_time = start_time + samples / samplerate

    return xr.DataArray(
        data=data,
        dims=("time", "channel"),
        coords={
            "time": np.linspace(
                start_time,
                end_time,
                data.shape[0],
                endpoint=False,
            ),
            "channel": range(data.shape[1]),
        },
        attrs={
            "recording_id": recording.uuid,
            "clip_id": clip.uuid,
            "path": recording.path,
            "time_units": "seconds",
            "time_expansion": recording.time_expansion,
            "samplerate": recording.samplerate,
        },
    )


def audio_to_bytes(
    data: np.ndarray,
    samplerate: int,
    bit_depth: int = 16,
) -> bytes:
    """Convert audio data to bytes."""
    buffer = BytesIO()
    with sf.SoundFile(
        buffer,
        mode="w",
        samplerate=samplerate,
        channels=data.shape[1],
        format="RAW",
        subtype=f"PCM_{bit_depth}",
    ) as fp:
        fp.write(data)
    return buffer.getvalue()
