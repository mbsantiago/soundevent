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

from soundevent import arrays, audio, data

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
#
# One of the nice things about using xarray is that it allows us to
# easily plot the spectrogram using the built-in plotting functions.

spectrogram.plot()

# %%
# The initial plot is hard to interpret due to the linear scale. Decibels (dB) 
# are more perceptually relevant for sound.
# Let's convert it to decibels using the
# [`arrays.to_db`][soundevent.arrays.to_db] function.

spectrogram_db = arrays.to_db(spectrogram)
spectrogram_db.plot()

# %%
# This is much better! We can now clearly see the frequency
# content evolving over time.
#
# To make subtle details even more apparent, we can apply a
# de-noising technique like PCEN (Per-Channel Energy
# Normalization). PCEN helps reduce background noise and
# enhance the target sounds. We can apply PCEN using the
# [`audio.pcen`][soundevent.audio.pcen] function.

pcen = audio.pcen(spectrogram)
pcen_db = arrays.to_db(pcen)
pcen_db.plot()

# %%
# In this case the PCEN transformation has not made a huge
# difference, but it can be very useful in other cases.
