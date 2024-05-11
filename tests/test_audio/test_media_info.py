"""Test suite for soundevent.audio.media_info module."""

from pathlib import Path

from soundevent.audio.media_info import (
    MediaInfo,
    compute_md5_checksum,
    compute_sha2_checksum,
    generate_wav_header,
    get_media_info,
)


def test_can_read_media_info(sample_24_bit_audio: Path):
    media_info = get_media_info(sample_24_bit_audio)

    assert isinstance(media_info, MediaInfo)
    assert media_info.format == "WAV"
    assert media_info.subtype == "PCM_24"
    assert media_info.duration_s == 19.4015625
    assert media_info.samplerate_hz == 96000
    assert media_info.channels == 1
    assert media_info.samples == 1862550


def test_can_generate_wav_header():
    """Example WAV header from http://soundfile.sapp.org/doc/WaveFormat/."""
    header = bytes.fromhex(
        "52 49 46 46 24 08 00 00 57 41 56 45 66 6d 74 20 10 00 "
        "00 00 01 00 02 00 22 56 00 00 88 58 01 00 04 00 10 00 "
        "64 61 74 61 00 08 00 00 00 00 00 00 24 17 1e f3 3c 13 "
        "3c 14 16 f9 18 f9 34 e7 23 a6 3c f2 24 f2 11 ce 1a 0d"
    )
    channels = 2
    samplerate = 22050
    bit_depth = 16
    samples = 2048 // (channels * bit_depth // 8)
    generated = generate_wav_header(samplerate, channels, samples, bit_depth)
    assert header[:44] == generated


def test_compute_hash_functions_succesfully(tmp_path: Path):
    path = tmp_path / "test_file.txt"
    path.write_text("This is a test file.")

    sha2 = compute_sha2_checksum(path)
    assert (
        sha2
        == "f29bc64a9d3732b4b9035125fdb3285f5b6455778edca72414671e0ca3b2e0de"
    )

    md5 = compute_md5_checksum(path)
    assert md5 == "3de8f8b0dc94b8c2230fab9ec0ba0506"
