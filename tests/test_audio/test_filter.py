"""Test suite for filtering functions."""

from unittest import mock

import numpy as np
import pytest
import xarray as xr
from scipy import signal

from soundevent import audio


def test_filter_audio_fails_if_no_samplerate():
    """Test that filter_audio fails if samplerate is missing."""
    data = xr.DataArray(np.random.randn(100), dims=["time"])
    with pytest.raises(ValueError):
        audio.filter(data, 16000)


def test_filter_audio_fails_if_not_an_xarray():
    """Test that filter_audio fails if not an xarray.DataArray."""
    data = np.random.randn(100)
    with pytest.raises(ValueError):
        audio.filter(data, 16000)  # type: ignore


def test_filter_audio_fails_if_no_time_axis():
    """Test that filter_audio fails with missing time axis."""
    data = xr.DataArray(
        np.random.randn(100),
        dims=["channel"],
        coords={"channel": range(100)},
        attrs={"samplerate": 16000},
    )
    with pytest.raises(ValueError):
        audio.filter(data, 16000)


def test_filter_audio_returns_an_xarray():
    """Test that filter_audio returns an xarray.DataArray."""
    data = xr.DataArray(
        np.random.randn(1000),
        dims=["time"],
        coords={"time": np.linspace(0, 1, 1000, endpoint=False)},
        attrs={"samplerate": 16000},
    )
    filtered = audio.filter(data, 1000)
    assert isinstance(filtered, xr.DataArray)


def test_filter_audio_preserves_attrs():
    """Test that filter_audio preserves attributes."""
    data = xr.DataArray(
        np.random.randn(1000),
        dims=["time"],
        coords={"time": np.linspace(0, 1, 1000, endpoint=False)},
        attrs={"samplerate": 16000, "other": "value"},
    )
    filtered = audio.filter(data, 1000)
    assert filtered.attrs == data.attrs


def test_filter_audio_fails_if_no_low_or_high_freq_provided():
    """Test filter_audio fails if low_freq and high_freq arent provided."""
    data = xr.DataArray(
        np.random.randn(1000),
        dims=["time"],
        coords={"time": np.linspace(0, 1, 1000, endpoint=False)},
        attrs={"samplerate": 16000, "other": "value"},
    )
    with pytest.raises(ValueError):
        audio.filter(data)


def test_filter_audio_applies_a_lowpass_filter():
    """Test that filter_audio applies a lowpass filter."""
    data = xr.DataArray(
        np.random.randn(1000),
        dims=["time"],
        coords={"time": np.linspace(0, 1, 1000, endpoint=False)},
        attrs={"samplerate": 16000},
    )

    mock_butter = mock.Mock(side_effect=signal.butter)
    with mock.patch.object(signal, "butter", mock_butter):
        audio.filter(data, high_freq=6000)
        mock_butter.assert_called_once_with(
            5,
            6000,
            btype="lowpass",
            fs=16000,
            output="sos",
        )


def test_filter_audio_applies_a_highpass_filter():
    """Test that filter_audio applies a highpass filter."""
    data = xr.DataArray(
        np.random.randn(1000),
        dims=["time"],
        coords={"time": np.linspace(0, 1, 1000, endpoint=False)},
        attrs={"samplerate": 16000},
    )

    mock_butter = mock.Mock(side_effect=signal.butter)
    with mock.patch.object(signal, "butter", mock_butter):
        audio.filter(data, low_freq=6000)
        mock_butter.assert_called_once_with(
            5,
            6000,
            btype="highpass",
            fs=16000,
            output="sos",
        )


def test_filter_audio_applies_a_bandpass_filter():
    """Test that filter_audio applies a bandpass filter."""
    data = xr.DataArray(
        np.random.randn(1000),
        dims=["time"],
        coords={"time": np.linspace(0, 1, 1000, endpoint=False)},
        attrs={"samplerate": 16000},
    )

    mock_butter = mock.Mock(side_effect=signal.butter)
    with mock.patch.object(signal, "butter", mock_butter):
        audio.filter(data, low_freq=1000, high_freq=6000)
        mock_butter.assert_called_once_with(
            5,
            [1000, 6000],
            btype="bandpass",
            fs=16000,
            output="sos",
        )
