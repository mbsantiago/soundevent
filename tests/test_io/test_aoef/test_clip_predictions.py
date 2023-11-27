"""Test suite for AOEF Clip Predictions Adapter."""

from soundevent import data
from soundevent.io.aoef.clip_predictions import (
    ClipPredictionsAdapter,
    ClipPredictionsObject,
)


def test_clip_predictions_can_be_converted_to_aoef(
    clip_predictions: data.ClipPrediction,
    clip_predictions_adapter: ClipPredictionsAdapter,
):
    """Test that a clip predictions can be converted to AOEF."""
    aoef = clip_predictions_adapter.to_aoef(clip_predictions)
    assert isinstance(aoef, ClipPredictionsObject)


def test_clip_predictions_is_recovered(
    clip_predictions: data.ClipPrediction,
    clip_predictions_adapter: ClipPredictionsAdapter,
):
    """Test that a clip predictions is recovered."""
    aoef = clip_predictions_adapter.to_aoef(clip_predictions)
    recovered = clip_predictions_adapter.to_soundevent(aoef)
    assert clip_predictions == recovered
