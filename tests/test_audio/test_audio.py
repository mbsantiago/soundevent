"""Test suite for audio loading functions."""
from pathlib import Path

import numpy as np
from uuid import uuid4
import pytest
import xarray as xr
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from scipy.io import wavfile

from soundevent import data
from soundevent.audio.io import load_clip, load_recording


@pytest.mark.parametrize("samplerate", [8_000, 16_000, 44_100, 256_000])
@pytest.mark.parametrize("duration", [0.1, 0.5, 1])
@pytest.mark.parametrize("channels", [1, 2])
@pytest.mark.parametrize("time_expansion", [1, 5, 10])
def test_load_recording(
    samplerate,
    duration,
    channels,
    random_wav,
    time_expansion,
):
    """Simple test for loading a recording."""
    # Arrange
    # Create a random wav file, with duration and samplerate adjusted
    # by the time expansion factor
    path = random_wav(
        samplerate=int(samplerate / time_expansion),
        duration=duration * time_expansion,
        channels=channels,
    )
    recording = data.Recording.from_file(path, time_expansion=time_expansion)

    # Act
    wav = load_recording(recording)

    # Assert
    # Check that the recording info is correct
    assert recording.path == path
    assert recording.samplerate == samplerate
    assert recording.duration == duration
    assert recording.channels == channels

    # Check that the loaded audio is correct
    assert isinstance(wav, xr.DataArray)
    assert wav.shape == (int(samplerate * duration), channels)
    assert wav.dtype == np.float32
    assert wav.dims == ("time", "channel")
    assert wav.coords["time"].shape == (int(samplerate * duration),)
    assert wav.coords["channel"].shape == (channels,)

    # Check that the wav has the correct metadata
    assert wav.attrs["samplerate"] == samplerate
    assert wav.attrs["time_expansion"] == time_expansion
    assert wav.attrs["time_units"] == "seconds"


@given(
    samplerate=st.sampled_from([8_000, 16_000, 44_100, 256_000]),
    channels=st.integers(min_value=1, max_value=2),
    clip_duration=st.decimals(min_value=0.01, max_value=1, places=6),
    clip_start=st.decimals(min_value=0, max_value=1, places=6),
    time_expansion=st.sampled_from([1, 5, 10, 20]),
)
@settings(
    suppress_health_check=(HealthCheck.function_scoped_fixture,),
)
def test_read_clip(
    tmp_path: Path,
    samplerate,
    channels,
    clip_duration,
    clip_start,
    time_expansion,
):
    """Test reading a clip from a recording."""
    # Arrange

    # Create a random wav for an audio of 2 seconds.
    samples = int(np.floor(samplerate * 2))
    wav = np.random.random((samples, channels)).astype(np.float32)

    # Save the wav to a file
    path = tmp_path / f"{uuid4()}.wav"

    # Save the wav with the adjusted samplerate
    adjusted_samplerate = int(np.floor(samplerate / time_expansion))
    wavfile.write(path, adjusted_samplerate, wav)

    recording = data.Recording(
        path=path,
        samplerate=samplerate,  # Real samplerate
        duration=2,
        channels=channels,
        time_expansion=time_expansion,
    )

    clip = data.Clip(
        recording=recording,
        start_time=clip_start,
        end_time=clip_start + clip_duration,
    )

    # Act
    clip_wav = load_clip(clip)

    # Assert
    clip_duration = clip.end_time - clip.start_time
    # Check that clip is the correct shape
    assert isinstance(clip_wav, xr.DataArray)
    assert clip_wav.shape == (
        int(np.ceil(samplerate * clip_duration)),
        channels,
    )
    assert clip_wav.dtype == np.float32
    assert clip_wav.dims == ("time", "channel")

    # Check that the wav has the correct metadata
    assert clip_wav.attrs["samplerate"] == samplerate
    assert clip_wav.attrs["time_expansion"] == time_expansion
    assert clip_wav.attrs["time_units"] == "seconds"

    # Check that the clip is the same as the original wav
    start_index = int(np.floor(clip.start_time * samplerate))
    clip_samples = int(np.ceil(clip_duration * samplerate))
    end_index = start_index + clip_samples
    assert np.allclose(clip_wav, wav[start_index:end_index, :])
    assert np.allclose(
        clip_wav.time,
        np.linspace(
            start_index / samplerate,
            end_index / samplerate,
            clip_wav.shape[0],
            endpoint=False,
        ),
    )

    # Check that we can slice the recording array to get the same clip
    # Load recording with xarray.
    rec_xr = load_recording(recording)
    assert rec_xr.attrs["samplerate"] == samplerate
    assert rec_xr.shape == (samples, channels)
    assert np.allclose(
        clip_wav.data,
        rec_xr.sel(time=clip_wav.time, method="nearest").data,
    )
