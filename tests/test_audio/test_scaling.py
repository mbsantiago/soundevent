"""Test suite for amplitude scaling functions."""

import numpy as np
import pytest
import xarray as xr

from soundevent import data
from soundevent.audio import (
    clamp_amplitude,
    compute_spectrogram,
    load_recording,
    pcen,
    scale_amplitude,
)


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


def test_scale_amplitude():
    array = xr.DataArray([1, 2, 3, 4, 5])
    scaled = scale_amplitude(array, scale="amplitude")
    assert (scaled == array).all()
    assert scaled.attrs["scale"] == "amplitude"


def test_scale_amplitude_when_using_power_scaling():
    array = xr.DataArray([1, 2, 3, 4, 5])
    scaled = scale_amplitude(array, scale="power")
    assert (scaled == array**2).all()
    assert scaled.attrs["scale"] == "power"


def test_scale_amplitude_when_using_db_scaling():
    array = xr.DataArray([1, 0.1, 0.01, 0.001, 0.0001])
    scaled = scale_amplitude(array, scale="dB")
    assert (scaled.data == np.array([0, -20, -40, -60, -80])).all()
    assert scaled.attrs["scale"] == "dB"


def test_scale_amplitude_fails_if_not_using_a_valid_scale():
    array = xr.DataArray([1, 2, 3, 4, 5])
    with pytest.raises(ValueError):
        scale_amplitude(array, scale="not_a_valid_scale")  # type: ignore


def test_can_run_pcen(
    random_wav,
):
    path = random_wav()
    recording = data.Recording.from_file(path)
    audio = load_recording(recording)
    spec = compute_spectrogram(audio, 0.02, 0.01)
    filtered = pcen(spec)

    assert isinstance(filtered, xr.DataArray)
    assert filtered.attrs["pcen"] is True
