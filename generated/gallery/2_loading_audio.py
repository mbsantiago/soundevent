"""
# Loading audio

One of the fundamental operations in computational bioacoustics is **reading**
audio files into a workable format. In `soundevent`, we use
[`xarray.DataArray`][xarray.DataArray] objects to hold loaded audio data.
[`xarray.DataArray`][xarray.DataArray] objects are an extension of
[`numpy`][numpy.ndarray] arrays, so there's no need to learn new concepts
if you are already familiar with [`numpy`][numpy.ndarray] arrays.


!!! note "Why use `xarray.DataArray` objects?"

    `xarray.DataArray` objects offer two key benefits: coordinates for easier
    referencing of time-related locations in the array, and the ability to
    store additional metadata such as `samplerate`, `time_expansion`, and
    specify that the temporal units are seconds. To learn more about
    `xarray.DataArray` objects, see the
    [xarray documentation](https://docs.xarray.dev/en/stable/getting-started-guide/why-xarray.html).


!!! note "Supported audio formats"

    `soundevent` supports most of the audio file formats supported by the
    [`soundfile`](https://python-soundfile.readthedocs.io/) library. Some
    formats were excluded because they do not support seeking and are not
    suitable for random access. This still includes most of the common audio
    file formats, such as WAV, FLAC, AIFF, and MP3. For a full list of
    supported formats, see the
    [audio.is_audio_file][soundevent.audio.is_audio_file] documentation.
"""

# %%
# ## Getting a Recording object
# To create a [`data.Recording`][soundevent.data.Recording] object from an
# audio file, you can use the
# [`from_file`][soundevent.data.Recording.from_file] method. This method
# extracts the metadata from the file and populates the `Recording` object with
# the relevant information.

from soundevent import data

recording = data.Recording.from_file("sample_audio.wav")
print(repr(recording))

# %%
# ## Loading the audio
# Once you have a [`data.Recording`][soundevent.data.Recording] object, you can
# load the audio data using the
# [`audio.load_recording`][soundevent.audio.load_recording] function:

from soundevent import audio

wav = audio.load_recording(recording)
print(wav)

# %%
# Note that the returned object is an [`xarray.DataArray`][xarray.DataArray]
# object with two dimensions: time and channel. The time coordinate represents
# the array of times in seconds corresponding to the samples in the
# xarray.DataArray object.

# %%
# ## Selecting clips from a recording
# You can use the [`sel`][xarray.DataArray.sel] method of xarray.DataArray to
# select a clip from the recording. This is useful when you have the full file
# loaded into memory and want to extract a specific clip:

# You can select a clip by specifying the start and end times in seconds.
subwav = wav.sel(time=slice(0, 1))
print(repr(subwav))

# %%
# Alternatively, if you only need to load a clip from the file without loading
# the entire file into memory, you can use the
# [`audio.load_clip`][soundevent.audio.load_clip] function:

clip = data.Clip(
    recording=recording,
    start_time=0,
    end_time=1,
)
subwav2 = audio.load_clip(clip)
print(repr(subwav2))

# %%
# In most cases, the results from `wav.sel` and `audio.load_clip` will be the
# same, except for the last sample. However, the difference is negligible, and
# the [`audio.load_clip`][soundevent.audio.load_clip] function is generally
# preferred for efficiency.
#
# You can verify the similarity of the clips:

import numpy as np

print(np.allclose(subwav[:-1], subwav2))
