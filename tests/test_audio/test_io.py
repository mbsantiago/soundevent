from pathlib import Path

from soundevent.audio.io import audio_to_bytes, load_audio


def test_audio_to_bytes(sample_24_bit_audio: Path):
    original_bytes = sample_24_bit_audio.read_bytes()[44:]  # ignore header
    audio, sr = load_audio(sample_24_bit_audio)
    result_bytes = audio_to_bytes(audio, sr, bit_depth=24)
    assert len(result_bytes) == len(original_bytes)
