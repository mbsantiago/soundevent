"""Functions for manipulating the amplitude scale of spectrograms."""

from typing import Literal

import librosa
import numpy as np
import xarray as xr

__all__ = [
    "clamp_amplitude",
    "scale_amplitude",
    "pcen",
]


AMPLITUDE_SCALES = Literal["amplitude", "power", "dB"]


def clamp_amplitude(
    spec: xr.DataArray,
    min_dB: float = -80.0,
    max_dB: float = 0.0,
) -> xr.DataArray:
    """Clamp amplitude values.

    All values below min_dB will be set to min_dB, and all values above max_dB
    will be set to max_dB.

    Parameters
    ----------
    spectogram
        Spectrogram with clamped amplitude values.
    min_dB : float
        Minimum amplitude value in dB. Defaults to -80.
    max_dB : float
        Maximum amplitude value in dB. Defaults to 0.

    Returns
    -------
    DataArray
        Clamped spectrogram image.
    """
    scale = spec.attrs.get("scale", "amplitude")

    if scale == "amplitude":
        min_dB = librosa.db_to_amplitude(min_dB)  # type: ignore
        max_dB = librosa.db_to_amplitude(max_dB)  # type: ignore

    if scale == "power":
        min_dB = librosa.db_to_power(min_dB)  # type: ignore
        max_dB = librosa.db_to_power(max_dB)  # type: ignore

    data = np.clip(spec.data, min_dB, max_dB)

    return xr.DataArray(
        data,
        dims=spec.dims,
        coords=spec.coords,
        attrs={
            **spec.attrs,
            "min_dB": min_dB,
            "max_dB": max_dB,
        },
    )


def scale_amplitude(
    spec: xr.DataArray,
    scale: AMPLITUDE_SCALES,
) -> xr.DataArray:
    """Scale spectrogram amplitude values.

    Parameters
    ----------
    spec : DataArray
        Spectrogram image.
    scale : str
        Scale to use for spectrogram computation, either "amplitude", "power",
        or "dB".

    Returns
    -------
    DataArray
        Scaled spectrogram.
    """
    data = spec.data

    if scale == "dB":
        data = librosa.amplitude_to_db(data, amin=1e-10)  # type: ignore

    elif scale == "power":
        data = data**2

    elif scale != "amplitude":
        raise ValueError(f"Invalid scale: {scale}")

    return xr.DataArray(
        data,
        dims=spec.dims,
        coords=spec.coords,
        attrs={
            **spec.attrs,
            "scale": scale,
        },
    )


def pcen(spec: xr.DataArray, **kwargs) -> xr.DataArray:
    """Apply PCEN to spectrogram.

    Parameters
    ----------
    spec
        Spectrogram to apply PCEN to.
    kwargs
        Keyword arguments to pass to librosa.pcen.

    Returns
    -------
    DataArray
        Spectrogram with PCEN applied.

    Notes
    -----
    Uses librosa.pcen implementation. If sr and hop_length are not provided,
    they will be inferred from the spectrogram attributes.
    """
    sr = spec.attrs["samplerate"]
    hop_length = int(spec.attrs["hop_size"] * sr)
    time_axis: int = spec.get_axis_num("time")  # type: ignore
    data = librosa.pcen(
        spec.data,
        **{
            "sr": sr,
            "hop_length": hop_length,
            "axis": time_axis,
            **kwargs,
        },
    )
    return xr.DataArray(
        data,
        dims=spec.dims,
        coords=spec.coords,
        attrs={
            **spec.attrs,
            "pcen": True,
        },
    )
