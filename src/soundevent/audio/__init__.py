"""Soundevent functions for handling audio files and arrays."""

from .files import is_audio_file
from .filter import filter_audio
from .io import load_audio, load_clip, load_recording
from .media_info import MediaInfo, compute_md5_checksum, get_media_info
from .resample import resample_audio
from .scaling import clamp_amplitude, pcen, scale_amplitude
from .spectrograms import compute_spectrogram

__all__ = [
    "MediaInfo",
    "compute_spectrogram",
    "compute_md5_checksum",
    "get_media_info",
    "load_audio",
    "load_clip",
    "load_recording",
    "is_audio_file",
    "resample_audio",
    "filter_audio",
    "scale_amplitude",
    "clamp_amplitude",
    "pcen",
]
