"""Functions for audio resampling."""

from typing import Optional

import xarray as xr
from scipy import signal

__all__ = [
    "resample",
]


def resample(
    audio: xr.DataArray,
    target_samplerate: int,
    window: Optional[str] = None,
) -> xr.DataArray:
    """Resample audio data to a target sample rate.

    This function assumes that the input audio object is a
    :class:`xarray.DataArray` with a "samplerate" attribute.

    Parameters
    ----------
    audio : xr.DataArray
        The audio data to resample. Should have a "samplerate" attribute,
        and a dimension named "time".

    target_samplerate : int
        The target sample rate of the audio data in Hz.

    window : str, optional
        The window to use for resampling. See scipy.signal.resample for
        details.

    Returns
    -------
    xr.DataArray
        The resampled audio data.

    Notes
    -----
    This function uses scipy.signal.resample to resample the audio data.

    Raises
    ------
    ValueError
        If the input audio object is not a :class:`xarray.DataArray`, or if
        it does not have a "samplerate" attribute, or if it does not have a
        "time" dimension.
    """
    if not isinstance(audio, xr.DataArray):
        raise ValueError("Audio must be an xarray.DataArray")

    if "samplerate" not in audio.attrs:
        raise ValueError("Audio must have a 'samplerate' attribute")

    if "time" not in audio.dims:
        raise ValueError("Audio must have a time dimension")

    time_axis: int = audio.get_axis_num("time")  # type: ignore
    samplerate = audio.attrs["samplerate"]
    ratio = target_samplerate / samplerate
    num_samples = int(audio.shape[time_axis] * ratio)
    times = audio.coords["time"].values

    resampled, resampled_times = signal.resample(  # type: ignore
        audio.values,
        num_samples,
        t=times,
        window=window,
        axis=time_axis,
    )

    return xr.DataArray(
        data=resampled,
        dims=audio.dims,
        coords={
            **audio.coords,
            "time": resampled_times,
        },
        attrs={
            **audio.attrs,
            "samplerate": target_samplerate,
        },
    )
