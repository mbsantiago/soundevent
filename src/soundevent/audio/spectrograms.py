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

DEFAULT_DIM_ORDER = ("frequency", "time", "channel")


def compute_spectrogram(
    audio: xr.DataArray,
    window_size: float,
    hop_size: float,
    window_type: str = "hann",
    detrend: Union[str, Callable, Literal[False]] = False,
    padded: bool = True,
    boundary: Optional[Literal["zeros", "odd", "even", "constant"]] = "zeros",
    scale: Literal["amplitude", "power", "psd"] = "psd",
    sort_dims: Union[tuple[str, ...], bool] = DEFAULT_DIM_ORDER,
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
    scale: Literal["amplitude", "power", "psd"], optional
        Specifies the scaling of the returned spectrogram values.
        Default is "psd".
        - "amplitude": Returns the magnitude of the STFT components.
          Units are typically the same as the input signal (e.g., V).
        - "power": Returns the squared magnitude of the STFT components.
          Units are the square of the input signal's units (e.g., V**2).
          This corresponds to the energy in each time-frequency bin,
          normalized for windowing effects but not frequency bin width.
        - "psd": Returns the Power Spectral Density. Units include per
          Hertz (e.g., V**2/Hz). This scaling accounts for windowing
          effects and frequency bin width, representing power density.
    sort_dims: Union[tuple[str, ...], bool], optional
        Controls the final dimension order of the output DataArray.
        - If `True`, transpose to `DEFAULT_DIM_ORDER`
          (currently ("frequency", "time", "channel")).
        - If a tuple of dimension names (e.g., ("channel", "frequency", "time")),
          transpose to that specific order. `missing_dims="ignore"` is used.
        - If `False`, do not transpose; return the array with the dimension
          order directly resulting from the STFT calculation (see Notes).
        Default is `DEFAULT_DIM_ORDER`.


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

    **Scaling Implementation:**
    * The different `scale` options leverage `scipy.signal.stft`'s `scaling`
        parameter and post-processing:
        - `scale="amplitude"` uses `stft(scaling='spectrum')` and computes `np.abs()`.
        - `scale="power"` uses `stft(scaling='spectrum')` and computes `np.abs()**2`.
        - `scale="psd"` uses `stft(scaling='psd')` and computes `np.abs()**2`.
    * Units mentioned in the `scale` parameter description assume the input
        signal `audio` has units of Volts (V) for illustrative purposes.

    **Dimension Ordering:**
    * The intermediate dimension order, before applying `sort_dims` (i.e.,
        the order if `sort_dims=False`), follows the structure where the
        original time dimension (`axis`) is replaced by the frequency dimension,
        and the new time segment dimension is appended last. For example, an
        input with dims `("height", "time", "channel")` results in an
        intermediate order of `("height", "frequency", "channel", "time")`.
    * By default (`sort_dims=True`), the output is transposed to match
        `DEFAULT_DIM_ORDER`, which is `("frequency", "time", "channel")`.

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
        scaling="psd" if scale == "psd" else "spectrum",
    )

    original_units = audio.attrs.get(ArrayAttrs.units.value, "V")
    if scale == "psd":
        # Compute the power spectral density
        spectrogram = np.abs(spectrogram) ** 2
        long_name = "Power Spectral Density Spectrogram"
        units = f"{original_units}**2/Hz"
    elif scale == "amplitude":
        spectrogram = np.abs(spectrogram)
        long_name = "Amplitude Spectrogram"
        units = f"{original_units}"
    elif scale == "power":
        spectrogram = np.abs(spectrogram) ** 2
        long_name = "Power Spectrogram"
        units = f"{original_units}**2"
    else:
        raise ValueError(
            f"Invalid scale option {scale}. Choose one of: "
            "psd, amplitude, power"
        )

    dims = (
        *[
            name
            if name != Dimensions.time.value
            else Dimensions.frequency.value
            for name in audio.dims
        ],
        Dimensions.time.value,
    )

    array = xr.DataArray(
        data=spectrogram,
        dims=dims,
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
            ArrayAttrs.units.value: units,
            ArrayAttrs.standard_name.value: "spectrogram",
            ArrayAttrs.long_name.value: long_name,
        },
    )

    if sort_dims:
        if not isinstance(sort_dims, tuple):
            sort_dims = DEFAULT_DIM_ORDER

        return array.transpose(..., *sort_dims, missing_dims="ignore")

    return array
