"""Test suite for AOEF Prediction Set Adapter."""

from pathlib import Path

from soundevent import data, io
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


def test_prediction_set_name_and_description_are_saved(
    tmp_path: Path,
    prediction_set: data.PredictionSet,
):
    """Test that the name and description of a prediction set are saved."""
    prediction_set = prediction_set.model_copy(
        update=dict(
            name="test_name",
            description="test description",
        )
    )

    # Save the prediction set to a file
    file_path = tmp_path / "test_aoef_prediction_set.json"
    io.save(prediction_set, file_path)

    # Load the prediction set from the file
    loaded_prediction_set = io.load(file_path)
    assert isinstance(loaded_prediction_set, data.PredictionSet)
    assert loaded_prediction_set.name == "test_name"
    assert loaded_prediction_set.description == "test description"
