"""Test suite for audio loading functions."""

from pathlib import Path
from uuid import uuid4

import numpy as np
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
    assert wav.dtype == np.float64
    assert wav.dims == ("time", "channel")
    assert wav.coords["time"].shape == (int(samplerate * duration),)
    assert wav.coords["channel"].shape == (channels,)


def test_load_recording_with_relative_path_and_audio_dir(
    tmp_path: Path, random_wav
):
    """Test loading a recording with a relative path and audio directory."""
    # Arrange
    # Create a random wav file
    filename = Path(f"{uuid4()}.wav")
    path = tmp_path / filename
    random_wav(path=path)

    # Create a recording with a relative path
    recording = data.Recording.from_file(path)
    recording.path = filename

    # Act
    wav = load_recording(recording, audio_dir=tmp_path)

    # Assert
    assert isinstance(wav, xr.DataArray)
    assert wav.shape == (
        int(recording.samplerate * recording.duration),
        recording.channels,
    )


def test_load_clip_with_relative_path_and_audio_dir(
    tmp_path: Path, random_wav
):
    """Test loading a clip with a relative path and audio directory."""
    # Arrange
    # Create a random wav file
    filename = Path(f"{uuid4()}.wav")
    path = tmp_path / filename
    random_wav(path=path)

    # Create a recording with a relative path
    recording = data.Recording.from_file(path)
    recording.path = filename

    clip = data.Clip(
        recording=recording,
        start_time=0.1,
        end_time=0.2,
    )

    # Act
    wav = load_clip(clip, audio_dir=tmp_path)

    # Assert
    assert isinstance(wav, xr.DataArray)
    assert wav.shape == (
        int(recording.samplerate * clip.duration),
        recording.channels,
    )


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
        int(np.floor(samplerate * clip_duration)),
        channels,
    )
    assert clip_wav.dtype == np.float64
    assert clip_wav.dims == ("time", "channel")

    # Check that the clip is the same as the original wav
    start_index = int(np.floor(clip.start_time * samplerate))
    clip_samples = int(np.floor(clip_duration * samplerate))
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
    assert rec_xr.shape == (samples, channels)
    assert np.allclose(
        clip_wav.data,
        rec_xr.sel(time=clip_wav.time, method="nearest").data,
    )


def test_can_load_clip_from_24_bit_depth_wav():
    """Test loading a 24 bit depth wav file."""
    # Arrange
    path = Path(__file__).parent / "24bitdepth.wav"

    recording = data.Recording.from_file(path)
    start_time = 0.5
    end_time = 1
    duration = end_time - start_time
    clip = data.Clip(
        recording=recording,
        start_time=start_time,
        end_time=end_time,
    )

    # Act
    wav = load_clip(clip)

    assert wav.shape == (recording.samplerate * duration, recording.channels)


def test_loading_clip_after_end_time_will_pad_with_zeros(
    random_wav,
):
    """Test loading a clip that is out of bounds."""
    # Arrange
    path = random_wav(
        samplerate=16_000,
        duration=1,
        channels=1,
    )

    recording = data.Recording.from_file(path)
    clip = data.Clip(
        recording=recording,
        start_time=0.5,
        end_time=1.5,
    )

    # Act
    wav = load_clip(clip)
    assert wav.shape == (recording.samplerate * 1, recording.channels)
    assert np.allclose(wav.sel(time=slice(1, None)), 0)


@pytest.mark.parametrize(
    "filename",
    [
        "aiff_alaw.aiff",
        "aiff_double.aiff",
        "aiff_float.aiff",
        "aiff_ima_adpcm.aiff",
        "aiff_pcm_16.aiff",
        "aiff_pcm_24.aiff",
        "aiff_pcm_32.aiff",
        "aiff_pcm_s8.aiff",
        "aiff_pcm_u8.aiff",
        "aiff_ulaw.aiff",
        "au_alaw.au",
        "au_double.au",
        "au_float.au",
        "au_pcm_16.au",
        "au_pcm_24.au",
        "au_pcm_32.au",
        "au_pcm_s8.au",
        "au_ulaw.au",
        "avr_pcm_16.avr",
        "avr_pcm_s8.avr",
        "avr_pcm_u8.avr",
        "caf_alac_16.caf",
        "caf_alac_20.caf",
        "caf_alac_24.caf",
        "caf_alac_32.caf",
        "caf_alaw.caf",
        "caf_double.caf",
        "caf_float.caf",
        "caf_pcm_16.caf",
        "caf_pcm_24.caf",
        "caf_pcm_32.caf",
        "caf_pcm_s8.caf",
        "caf_ulaw.caf",
        "flac_pcm_16.flac",
        "flac_pcm_24.flac",
        "flac_pcm_s8.flac",
        "htk_pcm_16.htk",
        "ircam_alaw.ircam",
        "ircam_float.ircam",
        "ircam_pcm_16.ircam",
        "ircam_pcm_32.ircam",
        "ircam_ulaw.ircam",
        "mat4_double.mat4",
        "mat4_float.mat4",
        "mat4_pcm_16.mat4",
        "mat4_pcm_32.mat4",
        "mat5_double.mat5",
        "mat5_float.mat5",
        "mat5_pcm_16.mat5",
        "mat5_pcm_32.mat5",
        "mat5_pcm_u8.mat5",
        "mp3_mpeg_layer_iii.mp3",
        "mpc2k_pcm_16.mpc2k",
        "nist_alaw.nist",
        "nist_pcm_16.nist",
        "nist_pcm_24.nist",
        "nist_pcm_32.nist",
        "nist_pcm_s8.nist",
        "nist_ulaw.nist",
        "ogg_opus.ogg",
        "ogg_vorbis.ogg",
        "paf_pcm_16.paf",
        "paf_pcm_24.paf",
        "paf_pcm_s8.paf",
        "pvf_pcm_16.pvf",
        "pvf_pcm_32.pvf",
        "pvf_pcm_s8.pvf",
        "rf64_alaw.rf64",
        "rf64_double.rf64",
        "rf64_float.rf64",
        "rf64_pcm_16.rf64",
        "rf64_pcm_24.rf64",
        "rf64_pcm_32.rf64",
        "rf64_pcm_u8.rf64",
        "rf64_ulaw.rf64",
        "sds_pcm_16.sds",
        "sds_pcm_24.sds",
        "sds_pcm_s8.sds",
        "svx_pcm_16.svx",
        "svx_pcm_s8.svx",
        "voc_alaw.voc",
        "voc_pcm_16.voc",
        "voc_pcm_u8.voc",
        "voc_ulaw.voc",
        "w64_alaw.w64",
        "w64_double.w64",
        "w64_float.w64",
        "w64_ima_adpcm.w64",
        "w64_ms_adpcm.w64",
        "w64_pcm_16.w64",
        "w64_pcm_24.w64",
        "w64_pcm_32.w64",
        "w64_pcm_u8.w64",
        "w64_ulaw.w64",
        "wav_alaw.wav",
        "wav_double.wav",
        "wav_float.wav",
        "wav_ima_adpcm.wav",
        "wav_ms_adpcm.wav",
        "wav_pcm_16.wav",
        "wav_pcm_24.wav",
        "wav_pcm_32.wav",
        "wav_pcm_u8.wav",
        "wav_ulaw.wav",
        "wavex_alaw.wavex",
        "wavex_double.wavex",
        "wavex_float.wavex",
        "wavex_pcm_16.wavex",
        "wavex_pcm_24.wavex",
        "wavex_pcm_32.wavex",
        "wavex_pcm_u8.wavex",
        "wavex_ulaw.wavex",
        "wve_alaw.wve",
    ],
)
def test_load_100ms_from_all_test_formats(filename):
    """Test loading 100ms from all test formats."""
    audio_dir = Path(__file__).parent / "data"
    recording = data.Recording.from_file(audio_dir / filename)
    clip = data.Clip(
        recording=recording,
        start_time=0.2,
        end_time=0.3,
    )
    wav = load_clip(clip)
    assert wav.shape == (
        np.floor(recording.samplerate * clip.duration),
        recording.channels,
    )
