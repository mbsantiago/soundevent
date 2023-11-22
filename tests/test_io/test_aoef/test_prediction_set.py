"""Test suite for AOEF Prediction Set Adapter."""

from soundevent import data
from soundevent.io.aoef.prediction_set import (
    PredictionSetAdapter,
    PredictionSetObject,
)


def test_prediction_set_can_be_converted_to_aoef(
    prediction_set: data.PredictionSet,
    prediction_set_adapter: PredictionSetAdapter,
):
    """Test that a prediction set can be converted to AOEF."""
    aoef = prediction_set_adapter.to_aoef(prediction_set)
    assert isinstance(aoef, PredictionSetObject)


def test_prediction_set_is_recovered(
    prediction_set: data.PredictionSet,
    prediction_set_adapter: PredictionSetAdapter,
):
    """Test that a prediction set is recovered."""
    aoef = prediction_set_adapter.to_aoef(prediction_set)
    recovered = prediction_set_adapter.to_soundevent(aoef)
    assert prediction_set == recovered
