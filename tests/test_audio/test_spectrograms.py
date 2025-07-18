"""Test suite for spectrograms functions."""

import numpy as np
import pytest
import xarray as xr

from soundevent import arrays, audio, data
from soundevent.audio.spectrograms import compute_spectrogram


@pytest.fixture
def sample_wave(random_wav):
    samplerate = 16000
    path = random_wav(samplerate=samplerate, duration=1)
    recording = data.Recording.from_file(path)
    return audio.load_recording(recording)


def test_compute_spectrograms_from_recordings(random_wav):
    """Test computing spectrograms from a random recording."""
    # Arrange
    samplerate = 16000
    window_size = 1024 / samplerate
    hop_size = 512 / samplerate

    path = random_wav(samplerate=samplerate, duration=1)
    recording = data.Recording.from_file(path)
    waveform = audio.load_recording(recording)

    # Act
    spectrogram = audio.compute_spectrogram(
        waveform,
        window_size=window_size,
        hop_size=hop_size,
    )

    # Assert
    # Is correct type
    assert isinstance(spectrogram, xr.DataArray)
    assert spectrogram.dtype == np.float64

    # Has correct dimensions
    assert spectrogram.dims == ("frequency", "time", "channel")
    assert spectrogram.shape == (513, 33, 1)

    # Has correct metadata
    assert spectrogram.attrs["window_size"] == window_size
    assert spectrogram.attrs["hop_size"] == hop_size
    assert spectrogram.attrs["window_type"] == "hann"

    # Has correct coordinates
    assert spectrogram.time.data[0] == 0.0
    assert np.abs(spectrogram.time.data[-1] - 1.0) < hop_size
    assert spectrogram.frequency.data[0] == 0.0
    assert spectrogram.frequency.data[-1] == samplerate / 2


def test_compute_spectrograms_from_clip(random_wav):
    """Test computing spectrograms from a random clip."""
    # Arrange
    samplerate = 16000
    window_size = 1024 / samplerate
    hop_size = 512 / samplerate

    path = random_wav(samplerate=samplerate, duration=1)
    recording = data.Recording.from_file(path)
    clip = data.Clip(recording=recording, start_time=0.1, end_time=0.9)
    waveform = audio.load_clip(clip)

    # Act
    spectrogram = audio.compute_spectrogram(
        waveform,
        window_size=window_size,
        hop_size=hop_size,
    )

    # Assert
    assert isinstance(spectrogram, xr.DataArray)

    # Has correct dimensions
    assert spectrogram.dims == ("frequency", "time", "channel")
    assert spectrogram.shape == (513, 26, 1)

    # Has correct metadata
    assert spectrogram.attrs["window_size"] == window_size
    assert spectrogram.attrs["hop_size"] == hop_size
    assert spectrogram.attrs["window_type"] == "hann"

    # Has correct coordinates
    assert spectrogram.time.data[0] == 0.1
    assert np.abs(spectrogram.time.data[-1] - 0.9) < hop_size


def test_spectrogram_has_correct_time_step(random_wav):
    # Arrange
    samplerate = 16000
    window_size = 1024 / samplerate
    hop_size = 512 / samplerate

    path = random_wav(samplerate=samplerate, duration=0.2)
    recording = data.Recording.from_file(path)
    clip = data.Clip(recording=recording, start_time=0.1, end_time=0.9)
    waveform = audio.load_clip(clip)

    # Act
    spectrogram = audio.compute_spectrogram(
        waveform,
        window_size=window_size,
        hop_size=hop_size,
    )

    step = arrays.estimate_dim_step(spectrogram.time)
    assert step == hop_size
    assert spectrogram.time.attrs["step"] == hop_size


def test_spectrogram_has_correct_frequency_step(random_wav):
    # Arrange
    samplerate = 16000
    nfft = 1024
    window_size = nfft / samplerate
    hop_size = 512 / samplerate

    path = random_wav(samplerate=samplerate, duration=0.2)
    recording = data.Recording.from_file(path)
    clip = data.Clip(recording=recording, start_time=0.1, end_time=0.9)
    waveform = audio.load_clip(clip)

    # Act
    spectrogram = audio.compute_spectrogram(
        waveform,
        window_size=window_size,
        hop_size=hop_size,
    )

    step = arrays.estimate_dim_step(spectrogram.frequency)
    assert step == samplerate / 1024
    assert spectrogram.frequency.attrs["step"] == samplerate / 1024


def test_can_compute_spectrogram_of_transposed_audio(random_wav):
    samplerate = 16000
    nfft = 1024
    window_size = nfft / samplerate
    hop_size = 512 / samplerate

    path = random_wav(samplerate=samplerate, duration=0.2)
    recording = data.Recording.from_file(path)
    clip = data.Clip(recording=recording, start_time=0.1, end_time=0.9)
    waveform = audio.load_clip(clip).T

    spectrogram = compute_spectrogram(
        waveform,
        window_size,
        hop_size,
        sort_dims=False,
    )
    assert spectrogram.ndim == 3
    assert spectrogram.dims == ("channel", "frequency", "time")


def test_spectrogram_dim_order():
    samplerate = 16_000
    nfft = 1024
    win_size = nfft / samplerate
    hop_size = 512 / samplerate
    times = np.linspace(0, 1, 16000)
    channels = np.array([0, 1])
    heights = np.arange(10)

    wave = xr.DataArray(
        np.random.random([len(heights), len(times), len(channels)]),
        dims=("height", "time", "channel"),
        coords={"height": heights, "time": times, "channel": channels},
    )

    spec = compute_spectrogram(wave, win_size, hop_size, sort_dims=False)
    assert spec.dims == ("height", "frequency", "channel", "time")

    wave = wave.transpose("height", "channel", "time")
    spec = compute_spectrogram(wave, win_size, hop_size, sort_dims=False)
    assert spec.dims == ("height", "channel", "frequency", "time")

    wave = wave.transpose("time", "channel", "height")
    spec = compute_spectrogram(wave, win_size, hop_size, sort_dims=False)
    assert spec.dims == ("frequency", "channel", "height", "time")


def test_can_compute_spectrogram_of_audio_without_channel_dim(random_wav):
    samplerate = 16000
    nfft = 1024
    window_size = nfft / samplerate
    hop_size = 512 / samplerate

    path = random_wav(samplerate=samplerate, duration=0.2)
    recording = data.Recording.from_file(path)
    clip = data.Clip(recording=recording, start_time=0.1, end_time=0.9)
    waveform = audio.load_clip(clip)
    waveform = waveform.sel(channel=0)

    spectrogram = compute_spectrogram(waveform, window_size, hop_size)
    assert spectrogram.ndim == 2
    assert spectrogram.dims == ("frequency", "time")


def test_can_compute_amplitude_spectrogram(sample_wave):
    samplerate = 16000
    nfft = 1024
    window_size = nfft / samplerate
    hop_size = 512 / samplerate
    spectrogram = compute_spectrogram(
        sample_wave,
        window_size,
        hop_size,
        scale="amplitude",
    )

    assert spectrogram.attrs["units"] == "V"
    assert spectrogram.attrs["long_name"] == "Amplitude Spectrogram"


def test_can_compute_power_spectrogram(sample_wave):
    samplerate = 16000
    nfft = 1024
    window_size = nfft / samplerate
    hop_size = 512 / samplerate
    spectrogram = compute_spectrogram(
        sample_wave,
        window_size,
        hop_size,
        scale="power",
    )

    assert spectrogram.attrs["units"] == "V**2"
    assert spectrogram.attrs["long_name"] == "Power Spectrogram"


def test_can_compute_psd_spectrogram(sample_wave):
    samplerate = 16000
    nfft = 1024
    window_size = nfft / samplerate
    hop_size = 512 / samplerate
    spectrogram = compute_spectrogram(
        sample_wave,
        window_size,
        hop_size,
        scale="psd",
    )

    assert spectrogram.attrs["units"] == "V**2/Hz"
    assert (
        spectrogram.attrs["long_name"] == "Power Spectral Density Spectrogram"
    )
