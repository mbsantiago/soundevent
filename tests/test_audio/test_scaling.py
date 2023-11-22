"""Test suite for amplitude scaling functions."""


import numpy as np
import xarray as xr

from soundevent.audio import clamp_amplitude


def test_clamp_amplitude():
    """Test clamp_amplitude function."""
    array = xr.DataArray(np.linspace(0, 1, 100))

    clamped = clamp_amplitude(array, min_dB=-80, max_dB=-20)

    assert clamped.min() == 0.0001
    assert clamped.max() == 0.1


def test_clamp_amplitude_when_using_power_scaling():
    """Test clamp_amplitude function when using power scaling."""
    array = xr.DataArray(np.linspace(0, 1, 100) ** 2)

    array.attrs["scale"] = "power"
    clamped = clamp_amplitude(array, min_dB=-40, max_dB=-20)
    assert clamped.min() == 0.0001
    assert clamped.max() == 0.01


def test_clamp_amplitude_when_using_db_scaling():
    """Test clamp_amplitude function when using db scaling."""
    array = xr.DataArray(np.linspace(-120, 0, 100))

    array.attrs["scale"] = "db"
    clamped = clamp_amplitude(array, min_dB=-40, max_dB=-20)
    assert clamped.min() == -40
    assert clamped.max() == -20
