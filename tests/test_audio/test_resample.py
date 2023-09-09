"""Test suite for resampling functions."""

import numpy as np
import pytest
import xarray as xr

from soundevent import audio


def test_resample_audio_fails_if_no_samplerate():
    """Test that resample_audio fails if samplerate is missing."""
    data = xr.DataArray(np.random.randn(100), dims=["time"])
    with pytest.raises(ValueError):
        audio.resample(data, 16000)


def test_resample_audio_fails_if_not_an_xarray():
    """Test that resample_audio fails if not an xarray.DataArray."""
    data = np.random.randn(100)
    with pytest.raises(ValueError):
        audio.resample(data, 16000)  # type: ignore


def test_resample_audio_fails_if_no_time_axis():
    """Test that resample_audio fails with missing time axis."""
    data = xr.DataArray(
        np.random.randn(100),
        dims=["channel"],
        coords={"channel": range(100)},
        attrs={"samplerate": 16000},
    )
    with pytest.raises(ValueError):
        audio.resample(data, 16000)


def test_resample_audio_returns_an_xarray():
    """Test that resample_audio returns an xarray.DataArray."""
    data = xr.DataArray(
        np.random.randn(1000),
        dims=["time"],
        coords={"time": np.linspace(0, 1, 1000, endpoint=False)},
        attrs={"samplerate": 16000},
    )
    resampled = audio.resample(data, 8000)
    assert isinstance(resampled, xr.DataArray)


def test_resample_audio_returns_correct_samplerate():
    """Test that resample_audio returns the correct samplerate."""
    data = xr.DataArray(
        np.random.randn(1000),
        dims=["time"],
        coords={"time": np.linspace(0, 1, 1000, endpoint=False)},
        attrs={"samplerate": 16000},
    )
    resampled = audio.resample(data, 8000)
    assert resampled.attrs["samplerate"] == 8000


def test_resample_audio_preserves_attrs():
    """Test that resample_audio preserves the attributes."""
    data = xr.DataArray(
        np.random.randn(1000),
        dims=["time"],
        coords={"time": np.linspace(0, 1, 1000, endpoint=False)},
        attrs={"samplerate": 16000, "other": "value"},
    )
    resampled = audio.resample(data, 8000)
    assert resampled.attrs["other"] == "value"


def test_resampled_audio_has_the_correct_time_coordinates():
    """Test that resample_audio returns the correct time coordinates."""
    data = xr.DataArray(
        np.random.randn(16000),
        dims=["time"],
        coords={"time": np.linspace(1, 2, 16000, endpoint=False)},
        attrs={"samplerate": 16000},
    )
    resampled = audio.resample(data, 8000)
    assert np.allclose(
        resampled.coords["time"].values,
        np.linspace(1, 2, 8000, endpoint=False),
    )


def test_resample_audio_preserves_dims():
    """Test that resample_audio preserves the dimensions."""
    data = xr.DataArray(
        np.random.randn(16000, 2, 3),
        dims=["time", "channel", "other"],
        coords={
            "time": np.linspace(1, 2, 16000, endpoint=False),
            "channel": range(2),
            "other": range(3),
        },
        attrs={"samplerate": 16000},
    )
    resampled = audio.resample(data, 8000)
    assert resampled.dims == data.dims


def test_resampling_is_done_in_the_time_axis():
    """Test that resampling is done in the time axis."""
    data = xr.DataArray(
        np.random.randn(2, 16000, 3),
        dims=["channel", "time", "other"],
        coords={
            "channel": range(2),
            "time": np.linspace(1, 2, 16000, endpoint=False),
            "other": range(3),
        },
        attrs={"samplerate": 16000},
    )
    resampled = audio.resample(data, 8000)
    assert resampled.shape == (2, 8000, 3)
