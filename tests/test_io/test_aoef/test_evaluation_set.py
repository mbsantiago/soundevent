"""Test suite for AOEF evaluation set adapter."""

from soundevent import data
from soundevent.io.aoef.evaluation_set import (
    EvaluationSetAdapter,
    EvaluationSetObject,
)


def test_evaluation_set_can_be_converted_to_aoef(
    evaluation_set: data.EvaluationSet,
    evaluation_set_adapter: EvaluationSetAdapter,
):
    """Test that an evaluation_set can be converted to AOEF."""
    aoef = evaluation_set_adapter.to_aoef(evaluation_set)
    assert isinstance(aoef, EvaluationSetObject)


def test_evaluation_set_is_recovered(
    evaluation_set: data.EvaluationSet,
    evaluation_set_adapter: EvaluationSetAdapter,
):
    """Test that an evaluation_set is recovered."""
    aoef = evaluation_set_adapter.to_aoef(evaluation_set)
    recovered = evaluation_set_adapter.to_soundevent(aoef)
    assert evaluation_set == recovered
