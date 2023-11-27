"""Test suite for AOEF Sequence Adapter."""

from soundevent import data
from soundevent.io.aoef.sequence import (
    SequenceAdapter,
    SequenceObject,
)


def test_sequence_can_be_converted_to_aoef(
    sequence: data.Sequence,
    sequence_adapter: SequenceAdapter,
):
    """Test that a sequence can be converted to AOEF."""
    aoef = sequence_adapter.to_aoef(sequence)
    assert isinstance(aoef, SequenceObject)


def test_sequence_is_recovered(
    sequence: data.Sequence,
    sequence_adapter: SequenceAdapter,
):
    """Test that a sequence can be recovered from AOEF."""
    aoef = sequence_adapter.to_aoef(sequence)
    recovered = sequence_adapter.to_soundevent(aoef)
    assert recovered == sequence
