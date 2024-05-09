"""Functions to compute several spectral representations of sound signals."""

from typing import Callable, Literal, Optional, Union

import numpy as np
import xarray as xr
from scipy import signal

from soundevent.arrays import (
    ArrayAttrs,
    Dimensions,
    create_frequency_dim_from_array,
    create_time_dim_from_array,
    get_dim_step,
)

__all__ = [
    "compute_spectrogram",
]


def compute_spectrogram(
    audio: xr.DataArray,
    window_size: float,
    hop_size: float,
    window_type: str = "hann",
    detrend: Union[str, Callable, Literal[False]] = False,
    padded: bool = True,
    boundary: Optional[Literal["zeros", "odd", "even", "constant"]] = "zeros",
) -> xr.DataArray:
    """Compute the spectrogram of a signal.

    This function calculates the short-time Fourier transform (STFT), which decomposes
    a signal into overlapping windows and computes the Fourier transform of each window.

    Parameters
    ----------
    audio: xr.DataArray
        The audio signal.
    window_size: float
        The duration of the STFT window in seconds.
    hop_size: float
        The duration of the STFT hop (in seconds). This determines the time
        step between consecutive STFT frames.
    window_type: str
        The type of window to use. Refer to
        [`scipy.signal.get_window`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.get_window.html)
        for supported types.
    detrend: Union[str, Callable, Literal[False]]
        Specifies how to detrend each STFT window. See
         [`scipy.signal.stft`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.stft.html)
         for options. Default is False (no detrending).
    padded: bool
        Indicates whether the input signal is zero-padded at the beginning and
        end before performing the STFT. See
        [`scipy.signal.stft`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.stft.html).
        Default is True.
    boundary: Optional[Literal["zeros", "odd", "even", "constant"]]
        Specifies the boundary extension mode for padding the signal to perform
        the STFT. See
        [`scipy.signal.stft`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.stft.html).
        Default is "zeros".

    Returns
    -------
    spectrogram : xr.DataArray
        The spectrogram of the audio signal. This is a three-dimensional
        xarray data array with the dimensions frequency, time, and channel.

    Notes
    -----
    **Time Bin Calculation:**
    *  The time axis of the spectrogram represents the center of each STFT window.
    *  The first time bin is centered at time t=hop_size / 2.
    *  Subsequent time bins are spaced by hop_size.
    """
    samplerate = 1 / get_dim_step(audio, Dimensions.time.value)
    time_axis: int = audio.get_axis_num(Dimensions.time.value)  # type: ignore
    nperseg = int(window_size * samplerate)
    noverlap = int((window_size - hop_size) * samplerate)

    # Compute the spectrogram
    frequencies, times, spectrogram = signal.stft(
        audio.data,
        fs=samplerate,
        window=window_type,
        nperseg=nperseg,
        noverlap=noverlap,
        return_onesided=True,
        axis=time_axis,
        detrend=detrend,  # type: ignore
        padded=padded,
        boundary=boundary,  # type: ignore
        scaling="psd",
    )

    # Compute the power spectral density
    psd = np.abs(spectrogram) ** 2

    return xr.DataArray(
        data=np.swapaxes(psd, 1, 2),
        dims=("frequency", "time", "channel"),
        coords={
            Dimensions.frequency.value: create_frequency_dim_from_array(
                frequencies,
                step=samplerate / nperseg,
            ),
            Dimensions.time.value: create_time_dim_from_array(
                times + audio.time.data[0],
                step=hop_size,
            ),
            Dimensions.channel.value: audio.channel,
        },
        attrs={
            **audio.attrs,
            "window_size": window_size,
            "hop_size": hop_size,
            "window_type": window_type,
            ArrayAttrs.units.value: "V**2/Hz",
            ArrayAttrs.standard_name.value: "spectrogram",
            ArrayAttrs.long_name.value: "Power Spectral Density",
        },
    )
