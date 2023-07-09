"""
# Computing spectrograms

After audio loading one of the most common operations within audio analysis
is to compute spectral representations of the audio signal. These attempt to
describe the signal in terms of its frequency content over time.

The most common spectral representation is the spectrogram. This is a
two-dimensional representation of the signal that shows the frequency content
of the signal over time. The spectrogram is computed by taking the short-time
Fourier transform (STFT) of the signal.

Here we will show how to compute spectrograms using the
[`audio.compute_spectrogram`][soundevent.audio.compute_spectrogram] function.

"""

# %%
# First, we will load a recording. We will use the
# the example recording from the (audio loading tutorial)[audio_loading].

from soundevent import audio, data

recording = data.Recording.from_file("sample_audio.wav")
wave = audio.load_recording(recording)
print(wave)

# %%
# Next, we will compute the spectrogram. Notice the spectrogram
# parameters are specified in terms of time, not samples. This is
# to facilitate working with audio signals that have different
# sample rates.

spectrogram = audio.compute_spectrogram(
    wave,
    window_size=0.064,
    hop_size=0.032,
)
print(spectrogram)

# %%
# Notice that the spectrogram is a three-dimensional
# [`xarray.DataArray`][xarray.DataArray]. The first dimension is
# *frequency*, the second is *time*, and the third is *channel*. The
# spectrogram is computed separately for each channel of the audio
# signal.
