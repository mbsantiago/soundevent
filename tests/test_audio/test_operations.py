"""Test suite for filtering functions."""

from unittest import mock

import numpy as np
import pytest
import xarray as xr
from scipy import signal

from soundevent import audio, data
from soundevent.arrays import create_time_range


@pytest.fixture
def example_data():
    return xr.DataArray(
        np.random.randn(1000),
        dims=["time"],
        coords={
            "time": create_time_range(
                start_time=0, end_time=1, samplerate=1000
            ),
        },
    )


def test_filter_audio_fails_if_low_freq_is_greater_than_high_freq(
    example_data,
):
    """Test that filter_audio fails if low_freq is greater than high_freq."""
    with pytest.raises(ValueError):
        audio.filter(example_data, low_freq=200, high_freq=100)


def test_filter_audio_fails_if_no_time_axis():
    """Test that filter_audio fails with missing time axis."""
    data = xr.DataArray(
        np.random.randn(100),
        dims=["channel"],
        coords={"channel": range(100)},
    )
    with pytest.raises(ValueError):
        audio.filter(data, 16000)


def test_filter_audio_returns_an_xarray(example_data: xr.DataArray):
    """Test that filter_audio returns an xarray.DataArray."""
    filtered = audio.filter(example_data, 200)
    assert isinstance(filtered, xr.DataArray)


def test_filter_audio_preserves_attrs(example_data: xr.DataArray):
    """Test that filter_audio preserves attributes."""
    filtered = audio.filter(example_data, 200)
    assert filtered.attrs == example_data.attrs


def test_filter_audio_fails_if_no_low_or_high_freq_provided(
    example_data: xr.DataArray,
):
    """Test filter_audio fails if low_freq and high_freq arent provided."""
    with pytest.raises(ValueError):
        audio.filter(example_data)


def test_filter_audio_applies_a_lowpass_filter(example_data: xr.DataArray):
    """Test that filter_audio applies a lowpass filter."""
    mock_butter = mock.Mock(side_effect=signal.butter)
    with mock.patch.object(signal, "butter", mock_butter):
        audio.filter(example_data, high_freq=200)
        mock_butter.assert_called_once_with(
            5,
            200,
            btype="lowpass",
            fs=1000,
            output="sos",
        )


def test_filter_audio_applies_a_highpass_filter(example_data: xr.DataArray):
    """Test that filter_audio applies a highpass filter."""
    mock_butter = mock.Mock(side_effect=signal.butter)
    with mock.patch.object(signal, "butter", mock_butter):
        audio.filter(example_data, low_freq=200)
        mock_butter.assert_called_once_with(
            5,
            200,
            btype="highpass",
            fs=1000,
            output="sos",
        )


def test_filter_audio_applies_a_bandpass_filter(example_data: xr.DataArray):
    """Test that filter_audio applies a bandpass filter."""
    mock_butter = mock.Mock(side_effect=signal.butter)
    with mock.patch.object(signal, "butter", mock_butter):
        audio.filter(example_data, low_freq=200, high_freq=400)
        mock_butter.assert_called_once_with(
            5,
            [200, 400],
            btype="bandpass",
            fs=1000,
            output="sos",
        )


def test_can_run_pcen(
    random_wav,
):
    path = random_wav()
    recording = data.Recording.from_file(path)
    wave = audio.load_recording(recording)
    spec = audio.compute_spectrogram(wave, 0.02, 0.01)
    filtered = audio.pcen(spec)

    assert isinstance(filtered, xr.DataArray)


def test_resample_audio_fails_if_no_time_axis():
    """Test that resample_audio fails with missing time axis."""
    data = xr.DataArray(
        np.random.randn(100),
        dims=["channel"],
        coords={"channel": range(100)},
    )
    with pytest.raises(ValueError):
        audio.resample(data, 16000)


def test_resample_audio_returns_an_xarray():
    """Test that resample_audio returns an xarray.DataArray."""
    data = xr.DataArray(
        np.random.randn(1000),
        dims=["time"],
        coords={"time": np.linspace(0, 1, 1000, endpoint=False)},
    )
    resampled = audio.resample(data, 8000)
    assert isinstance(resampled, xr.DataArray)


def test_resample_audio_preserves_attrs():
    """Test that resample_audio preserves the attributes."""
    data = xr.DataArray(
        np.random.randn(1000),
        dims=["time"],
        coords={"time": np.linspace(0, 1, 1000, endpoint=False)},
        attrs={"other": "value"},
    )
    resampled = audio.resample(data, 8000)
    assert resampled.attrs["other"] == "value"


def test_resampled_audio_has_the_correct_time_coordinates():
    """Test that resample_audio returns the correct time coordinates."""
    data = xr.DataArray(
        np.random.randn(16000),
        dims=["time"],
        coords={"time": np.linspace(1, 2, 16000, endpoint=False)},
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
    )
    resampled = audio.resample(data, 8000)
    assert resampled.shape == (2, 8000, 3)


def test_pcen_audio_fails_if_dimension_does_not_exist():
    """Test that pcen_audio fails if the time dimension does not exist."""
    data = xr.DataArray(
        np.random.randn(100),
        dims=["channel"],
        coords={"channel": range(100)},
    )
    with pytest.raises(ValueError):
        audio.pcen(data)


def test_pcen_fails_with_negative_parameters(example_data):
    """Test that pcen fails with negative parameters."""
    with pytest.raises(ValueError):
        audio.pcen(example_data, bias=-1)

    with pytest.raises(ValueError):
        audio.pcen(example_data, gain=-1)

    with pytest.raises(ValueError):
        audio.pcen(example_data, eps=-1e-10)

    with pytest.raises(ValueError):
        audio.pcen(example_data, smooth=-1)
