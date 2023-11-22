"""Test suite for AOEF Clip Adapter."""

from soundevent import data
from soundevent.io.aoef.clip import ClipAdapter, ClipObject


def test_clip_can_be_converted_to_aoef(
    clip: data.Clip,
    clip_adapter: ClipAdapter,
):
    """Test that a clip can be converted to AOEF."""
    aoef = clip_adapter.to_aoef(clip)
    assert isinstance(aoef, ClipObject)


def test_clip_is_recovered(
    clip: data.Clip,
    clip_adapter: ClipAdapter,
):
    """Test that a clip is recovered."""
    aoef = clip_adapter.to_aoef(clip)
    recovered = clip_adapter.to_soundevent(aoef)
    assert clip == recovered
