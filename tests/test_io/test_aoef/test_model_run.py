"""Test suite for AOEF Model Run Adapter."""

from soundevent import data
from soundevent.io.aoef.model_run import ModelRunAdapter, ModelRunObject


def test_model_run_can_be_converted_to_aoef(
    model_run: data.ModelRun,
    model_run_adapter: ModelRunAdapter,
):
    """Test that a model run can be converted to AOEF."""
    aoef = model_run_adapter.to_aoef(model_run)
    assert isinstance(aoef, ModelRunObject)


def test_model_run_is_recovered(
    model_run: data.ModelRun,
    model_run_adapter: ModelRunAdapter,
):
    """Test that a model run is recovered."""
    aoef = model_run_adapter.to_aoef(model_run)
    recovered = model_run_adapter.to_soundevent(aoef)
    assert model_run == recovered
