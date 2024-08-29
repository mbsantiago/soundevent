from typing import Optional

import numpy as np
import xarray as xr
from scipy import signal

from soundevent.arrays import (
    Dimensions,
    create_time_dim_from_array,
    get_dim_step,
)

__all__ = [
    "filter",
    "resample",
    "pcen",
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
    dim: str = Dimensions.time.value,
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
    dim : str, optional
        The dimension along which to filter the audio data. By default,
        "time".

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
    if dim not in audio.dims:
        raise ValueError(f"Audio must have a {dim} dimension")

    axis = audio.get_axis_num(dim)
    step = get_dim_step(audio, dim)
    samplerate = int(1 / step)

    sos = _get_filter(
        samplerate,
        low_freq,
        high_freq,
        order,
    )
    filtered = signal.sosfiltfilt(
        sos,
        audio.data,
        axis=axis,  # type: ignore
    )

    return xr.DataArray(
        data=filtered,
        dims=audio.dims,
        coords=audio.coords,
        attrs=audio.attrs,
    )


def resample(
    array: xr.DataArray,
    target_samplerate: int,
    window: Optional[str] = None,
    dim: str = Dimensions.time.value,
) -> xr.DataArray:
    """Resample array data to a target sample rate along a given dimension.

    Parameters
    ----------
    array
        The data array to resample.
    target_samplerate
        The target sample rate of the resampled data in Hz.
    window
        The window to use for resampling. See
        [scipy.signal.resample][scipy.signal.resample] for details.
    dim
        The dimension along which to resample the audio data. By default,
        "time".

    Returns
    -------
    xr.DataArray
        The resampled audio data.

    Notes
    -----
    This function uses [scipy.signal.resample][scipy.signal.resample] to
    resample the input data array to the target sample rate. This function
    uses the Fourier method to resample the data, which is suitable for
    resampling audio data. For other resampling methods, consider using
    the [xarray.DataArray.interp][xarray.DataArray.interp] method.

    Raises
    ------
    ValueError
        If the input audio object is not a :class:`xarray.DataArray`, or if
        it does not have a "samplerate" attribute, or if it does not have a
        "time" dimension.
    """
    if dim not in array.dims:
        raise ValueError(f"Audio must have a {dim} dimension")

    time_axis = array.get_axis_num(dim)
    step = get_dim_step(array, dim)
    ratio = target_samplerate * step
    times = array.coords[dim].values
    num_samples = int(times.size * ratio)

    resampled, resampled_times = signal.resample(
        array.values,
        num_samples,
        t=times,
        window=window,
        axis=time_axis,  # type: ignore
    )

    return xr.DataArray(
        data=resampled,
        dims=array.dims,
        coords={
            **array.coords,
            Dimensions.time.value: create_time_dim_from_array(
                resampled_times,
                step=1 / target_samplerate,
            ),
        },
        attrs=array.attrs,
    )


def pcen(
    array: xr.DataArray,
    smooth: float = 0.025,
    gain: float = 0.98,
    bias: float = 2,
    power: float = 0.5,
    eps: float = 1e-6,
    dim: str = Dimensions.time.value,
) -> xr.DataArray:
    r"""Apply PCEN to spectrogram.

    Parameters
    ----------
    array
        The spectrogram to which to apply PCEN.
    smooth
        The time constant for smoothing the input spectrogram. By default,
        0.025.
    gain
        The gain factor for the PCEN transform. By default, 0.98.
    bias
        The bias factor for the PCEN transform. By default, 2.
    power
        The power factor for the PCEN transform. By default, 0.5.
    eps
        An epsilon value to prevent division by zero. By default, 1e-6.
    dim
        The dimension along which to apply PCEN.

    Returns
    -------
    DataArray
        Spectrogram with PCEN applied.

    Notes
    -----
    This function applies the Per-Channel Energy Normalization (PCEN) transform
    to a spectrogram, as described in [1].

    The PCEN transform is defined as:

    $$
    PCEN(X) = \left(\frac{X}{(\epsilon + S)^{\alpha}} + \delta\right)^r - \delta^r
    $$

    where $X$ is the input spectrogram, $S$ is the smoothed version of the
    input spectrogram, $\alpha$ is the power factor, $\delta$ is the bias
    factor, and $r$ is the gain factor.

    The smoothed version of the input spectrogram is computed using a
    first-order IIR filter:

    $$
    S_t = (1 - \beta) S_{t-1} + \beta X_t
    $$

    where $\beta$ is the smoothing factor.

    The default values for the parameters are taken from the PCEN paper [1].

    References
    ----------
    [1] Wang, Y., Getreuer, P., Hughes, T., Lyon, R. F., & Saurous, R. A.
    (2017, March). Trainable frontend for robust and far-field keyword
    spotting. In 2017 IEEE International Conference on Acoustics, Speech and
    Signal Processing (ICASSP) (pp. 5670-5674). IEEE.

    """
    if dim not in array.dims:
        raise ValueError(f"Spectrogram must have a {dim} dimension")

    if eps <= 0:
        raise ValueError("eps must be greater than zero")

    if smooth <= 0:
        raise ValueError("smooth must be greater than zero")

    if gain <= 0:
        raise ValueError("gain must be greater than zero")

    if bias <= 0:
        raise ValueError("bias must be greater than zero")

    axis = array.get_axis_num(dim)

    # Smooth the input array along the given axis
    smoothed: np.ndarray = signal.lfilter(
        [smooth],
        [1, smooth - 1],
        array.data,
        axis=axis,  # type: ignore
    )

    smooth = np.exp(-gain * (np.log(eps) + np.log1p(smoothed / eps)))
    data = (bias**power) * np.expm1(
        power * np.log1p(array.data * smooth / bias)
    )

    return xr.DataArray(
        data,
        dims=array.dims,
        coords=array.coords,
        attrs=array.attrs,
    )
