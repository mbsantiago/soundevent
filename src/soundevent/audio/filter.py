"""Funtions for audio filtering."""

from typing import Optional

import numpy as np
import xarray as xr
from scipy import signal

__all__ = [
    "filter",
]


def _get_filter(
    samplerate: int,
    low_freq: Optional[float] = None,
    high_freq: Optional[float] = None,
    order: int = 5,
) -> np.ndarray:
    if low_freq is None and high_freq is None:
        raise ValueError(
            "At least one of low_freq and high_freq must be specified."
        )

    if low_freq is None:
        # Low pass filter
        return signal.butter(
            order,
            high_freq,
            btype="lowpass",
            output="sos",
            fs=samplerate,
        )

    if high_freq is None:
        # High pass filter
        return signal.butter(
            order,
            low_freq,
            btype="highpass",
            output="sos",
            fs=samplerate,
        )

    if low_freq > high_freq:
        raise ValueError("low_freq must be less than high_freq.")

    # Band pass filter
    return signal.butter(
        order,
        [low_freq, high_freq],
        btype="bandpass",
        output="sos",
        fs=samplerate,
    )


def filter(
    audio: xr.DataArray,
    low_freq: Optional[float] = None,
    high_freq: Optional[float] = None,
    order: int = 5,
) -> xr.DataArray:
    """Filter audio data.

    This function assumes that the input audio object is a
    :class:`xarray.DataArray` with a "samplerate" attribute and a "time"
    dimension.

    The filtering is done using a Butterworth filter or the specified order.
    The type of filter (lowpass/highpass/bandpass filter) is determined
    by the specified cutoff frequencies. If only one cutoff frequency is
    specified, a low pass or high pass filter is used. If both cutoff
    frequencies are specified, a band pass filter is used.

    Parameters
    ----------
    audio : xr.DataArray
        The audio data to filter with a "samplerate" attribute and
        a "time" dimension.
    low_freq : float, optional
        The low cutoff frequency in Hz.
    high_freq : float, optional
        The high cutoff frequency in Hz.
    order : int, optional
        The order of the filter. By default, 5.

    Returns
    -------
    xr.DataArray
        The filtered audio data.

    Raises
    ------
    ValueError
        If neither low_freq nor high_freq is specified, or if both
        are specified and low_freq > high_freq.

    """
    if not isinstance(audio, xr.DataArray):
        raise ValueError("Audio must be an xarray.DataArray")

    if "samplerate" not in audio.attrs:
        raise ValueError("Audio must have a 'samplerate' attribute")

    if "time" not in audio.dims:
        raise ValueError("Audio must have a time dimension")

    axis: int = audio.get_axis_num("time")  # type: ignore
    sos = _get_filter(
        audio.attrs["samplerate"],
        low_freq,
        high_freq,
        order,
    )

    filtered = signal.sosfiltfilt(sos, audio.data, axis=axis)
    return xr.DataArray(
        data=filtered,
        dims=audio.dims,
        coords=audio.coords,
        attrs=audio.attrs,
    )
