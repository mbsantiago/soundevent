"""Functions to compute several spectral representations of sound signals."""

import numpy as np
import xarray as xr


def generate_spectrogram(
    audio: xr.DataArray,
    window_size: int,
    overlap: float,
    window_type="hann",
) -> xr.DataArray:
    """Compute the spectrogram of a signal."""
    pass
