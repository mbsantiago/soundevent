"""Test suite for AOEF Evaluation Adapter."""

from soundevent import data
from soundevent.io.aoef.evaluation import EvaluationAdapter, EvaluationObject


def test_evaluation_can_be_converted_to_aoef(
    evaluation: data.Evaluation,
    evaluation_adapter: EvaluationAdapter,
):
    """Test that an evaluation can be converted to AOEF."""
    aoef = evaluation_adapter.to_aoef(evaluation)
    assert isinstance(aoef, EvaluationObject)


def test_evaluation_is_recovered(
    evaluation: data.Evaluation,
    evaluation_adapter: EvaluationAdapter,
):
    """Test that an evaluation is recovered."""
    aoef = evaluation_adapter.to_aoef(evaluation)
    recovered = evaluation_adapter.to_soundevent(aoef)
    assert evaluation == recovered
