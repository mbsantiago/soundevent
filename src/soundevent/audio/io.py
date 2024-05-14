"""Input and output functions for soundevent.

Currently only supports reading and writing of .wav files.
"""

from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import soundfile as sf
import xarray as xr

from soundevent import data
from soundevent.arrays import ArrayAttrs, Dimensions, create_time_range
from soundevent.audio.attributes import AudioAttrs

__all__ = [
    "load_audio",
    "load_recording",
    "load_clip",
]


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

    with sf.SoundFile(path) as fp:
        fp.seek(offset)
        data = fp.read(frames=samples, always_2d=True, fill_value=0)
        samplerate = fp.samplerate
        return data, samplerate


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
        dims=(Dimensions.time.value, Dimensions.channel.value),
        coords={
            Dimensions.time.value: create_time_range(
                start_time=0,
                end_time=recording.duration,
                samplerate=recording.samplerate,
            ),
            Dimensions.channel.value: range(data.shape[1]),
        },
        attrs={
            AudioAttrs.recording_id.value: str(recording.uuid),
            AudioAttrs.path.value: str(recording.path),
            ArrayAttrs.units.value: "V",
            ArrayAttrs.standard_name.value: "amplitude",
            ArrayAttrs.long_name.value: "Amplitude",
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
    samples = int(np.floor(duration * samplerate))

    path = recording.path
    if audio_dir is not None:
        path = Path(audio_dir) / path

    data, _ = load_audio(
        path,
        offset=offset,
        samples=samples,
    )

    # NOTE: Adjust start and end time to be on sample boundaries. This is
    # necessary because the specified start and end time might not align
    # precisely with the sampling moments of the audio. By aligning with the
    # sample boundaries, we ensure that any time location within the clip,
    # relative to the original audio file, remains accurate.
    start_time = offset / samplerate
    end_time = start_time + samples / samplerate

    return xr.DataArray(
        data=data,
        dims=(Dimensions.time.value, Dimensions.channel.value),
        coords={
            Dimensions.time.value: create_time_range(
                start_time=start_time,
                end_time=end_time,
                samplerate=samplerate,
            ),
            Dimensions.channel.value: range(data.shape[1]),
        },
        attrs={
            AudioAttrs.recording_id.value: str(recording.uuid),
            AudioAttrs.clip_id.value: str(clip.uuid),
            AudioAttrs.path.value: str(recording.path),
            ArrayAttrs.units.value: "V",
            ArrayAttrs.standard_name.value: "amplitude",
            ArrayAttrs.long_name.value: "Amplitude",
        },
    )


PCM_SUBTYPES = {
    8: "PCM_S8",
    16: "PCM_16",
    24: "PCM_24",
    32: "PCM_32",
}


def audio_to_bytes(
    data: np.ndarray,
    samplerate: int,
    bit_depth: int = 16,
) -> bytes:
    """Convert audio data to bytes."""
    buffer = BytesIO()
    subtype = PCM_SUBTYPES.get(bit_depth)
    if subtype is None:
        raise ValueError(
            "Unsupported bit depth: {bit_depth}. "
            "Valid bit depths are: {PCM_SUBTYPES.keys()}."
        )
    with sf.SoundFile(
        buffer,
        mode="w",
        samplerate=samplerate,
        channels=data.shape[1],
        format="RAW",
        subtype=subtype,
    ) as fp:
        fp.write(data)
    return buffer.getvalue()
