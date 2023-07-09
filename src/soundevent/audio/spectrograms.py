"""Functions to compute several spectral representations of sound signals."""

import numpy as np
import xarray as xr
from scipy import signal


def compute_spectrogram(
    audio: xr.DataArray,
    window_size: float,
    hop_size: float,
    window_type="hann",
) -> xr.DataArray:
    """Compute the spectrogram of a signal.

    Parameters
    ----------
    audio : xr.DataArray
        The audio signal. We are assuming that this has two dimensions: time
        and channel. The time dimension should be the first dimension. Also,
        the data array should have a sample rate attribute. This is
        automatically True if the audio signal is loaded using
        [`audio.load_recording`][soundevent.audio.load_recording].
    window_duration : float
        The duration of the STFT window in seconds.
    hop_duration : float
        The duration of the STFT hop in seconds.
    window_type : str, optional
        The type of window to use. This should be one of the window types
        supported by [`scipy.signal.get_window`][scipy.signal.get_window].
    """
    # Get the sample rate
    sample_rate = audio.attrs["samplerate"]

    # Compute the number of samples in each window
    nperseg = int(window_size * sample_rate)

    # Compute the number of samples to overlap
    noverlap = int((window_size - hop_size) * sample_rate)

    # Compute the window
    window = signal.get_window(window_type, nperseg)

    # Compute the spectrogram
    frequencies, times, spectrogram = signal.spectrogram(
        audio.data,
        fs=sample_rate,
        window=window,
        nperseg=nperseg,
        noverlap=noverlap,
        axis=0,
    )

    # Convert to xarray
    return xr.DataArray(
        data=np.swapaxes(spectrogram, 1, 2),
        dims=("frequency", "time", "channel"),
        coords={
            "frequency": frequencies,
            # The times returned by scipy.signal.spectrogram are
            # relative to the start of the signal and are the center
            # times of each window. We need to add the start time of
            # the signal and subtract half of the window size to get
            # the times relative to the start of the recording.
            "time": times + audio.time.data[0] - window_size / 2,
            "channel": audio.channel,
        },
        attrs={
            "samplerate": sample_rate,
            "window_size": window_size,
            "hop_size": hop_size,
            "window_type": window_type,
        },
    )
