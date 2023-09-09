"""Input and output functions for soundevent.

Currently only supports reading and writing of .wav files.
"""

import os
from typing import Optional, Tuple

import numpy as np
import xarray as xr
from scipy.io import wavfile

from soundevent.data.clips import Clip
from soundevent.data.recordings import Recording

__all__ = [
    "load_audio",
    "load_recording",
]


def load_audio(
    path: os.PathLike,
    offset: int = 0,
    samples: Optional[int] = None,
) -> Tuple[np.ndarray, int]:
    """Load an audio file.

    Parameters
    ----------
    path : Path
        The path to the audio file.
    offset : int, optional
        The offset in samples from the start of the audio file.
    samples : int, optional
        The number of samples to load. If None, load the entire file.

    Returns
    -------
    np.ndarray
        The audio data.
    samplerate : int
        The sample rate of the audio file in Hz.

    """
    if offset == 0 and samples is None:
        samplerate, data = wavfile.read(path, mmap=False)
    else:
        samplerate, mmap = wavfile.read(path, mmap=True)

        if samples is None:
            end_index = None
        else:
            end_index = offset + samples

        data = mmap[offset:end_index]

    # Add channel dimension if necessary
    if data.ndim == 1:
        data = data[:, None]

    # Convert to float if necessary
    if data.dtype == "int16":
        data = data.astype("float32") / np.iinfo("int16").max
    if data.dtype == "int32":
        data = data.astype("float32") / np.iinfo("int32").max

    return data, samplerate


def load_recording(recording: Recording) -> xr.DataArray:
    """Load a recording from a file.

    Parameters
    ----------
    recording : data.Recording
        The recording to load.

    Returns
    -------
    xr.DataArray
        The loaded recording.

    """
    data, _ = load_audio(recording.path)
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
            "recording_id": recording.id,
            "time_units": "seconds",
            "time_expansion": recording.time_expansion,
            "samplerate": recording.samplerate,
        },
    )


def load_clip(clip: Clip) -> xr.DataArray:
    """Load a clip from a file.

    Parameters
    ----------
    clip : data.Clip
        The clip to load.

    Returns
    -------
    xr.DataArray
        The loaded clip. The returned clip stores the samplerate
        and time expansion of the recording from which it was
        extracted.
    """
    recording = clip.recording
    samplerate = recording.samplerate

    offset = int(np.floor(clip.start_time * samplerate))
    duration = clip.end_time - clip.start_time
    samples = int(np.ceil(duration * samplerate))

    data, _ = load_audio(
        recording.path,
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
            "recording_id": recording.id,
            "time_units": "seconds",
            "time_expansion": recording.time_expansion,
            "samplerate": recording.samplerate,
        },
    )
