"""Test suite for AOEF Sequence Prediction Adapter."""

from soundevent import data
from soundevent.io.aoef.sequence_prediction import (
    SequencePredictionAdapter,
    SequencePredictionObject,
)


def test_sequence_prediction_can_be_converted_to_aoef(
    sequence_prediction: data.SequencePrediction,
    sequence_prediction_adapter: SequencePredictionAdapter,
):
    """Test that a sequence prediction can be converted to AOEF."""
    aoef = sequence_prediction_adapter.to_aoef(sequence_prediction)
    assert isinstance(aoef, SequencePredictionObject)


def test_sequence_prediction_is_recovered(
    sequence_prediction: data.SequencePrediction,
    sequence_prediction_adapter: SequencePredictionAdapter,
):
    """Test that a sequence prediction can be recovered from AOEF."""
    aoef = sequence_prediction_adapter.to_aoef(sequence_prediction)
    recovered = sequence_prediction_adapter.to_soundevent(aoef)
    assert recovered == sequence_prediction
