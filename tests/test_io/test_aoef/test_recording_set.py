"""Test suite for AOEF Recording Set Adapter."""

from soundevent import data
from soundevent.io.aoef.recording_set import (
    RecordingSetAdapter,
    RecordingSetObject,
)


def test_recording_set_can_be_converted_to_aoef(
    recording_set: data.RecordingSet,
    recording_set_adapter: RecordingSetAdapter,
):
    """Test that a recording set can be converted to AOEF."""
    aoef = recording_set_adapter.to_aoef(recording_set)
    assert isinstance(aoef, RecordingSetObject)


def test_recording_set_is_recovered(
    recording_set: data.RecordingSet,
    recording_set_adapter: RecordingSetAdapter,
):
    """Test that a recording set is recovered."""
    aoef = recording_set_adapter.to_aoef(recording_set)
    recovered = recording_set_adapter.to_soundevent(aoef)
    assert recording_set == recovered
