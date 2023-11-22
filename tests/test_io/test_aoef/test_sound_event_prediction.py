"""Test suite for AOEF Sound Event Prediction Adapter."""

from soundevent import data
from soundevent.io.aoef.sound_event_prediction import (
    SoundEventPredictionAdapter,
    SoundEventPredictionObject,
)


def test_sound_event_prediction_can_be_converted_to_aoef(
    sound_event_prediction: data.SoundEventPrediction,
    sound_event_prediction_adapter: SoundEventPredictionAdapter,
):
    """Test that a sound event prediction can be converted to AOEF."""
    aoef = sound_event_prediction_adapter.to_aoef(sound_event_prediction)
    assert isinstance(aoef, SoundEventPredictionObject)


def test_sound_event_prediction_is_recovered(
    sound_event_prediction: data.SoundEventPrediction,
    sound_event_prediction_adapter: SoundEventPredictionAdapter,
):
    """Test that a sound event prediction is recovered."""
    aoef = sound_event_prediction_adapter.to_aoef(sound_event_prediction)
    recovered = sound_event_prediction_adapter.to_soundevent(aoef)
    assert sound_event_prediction == recovered
