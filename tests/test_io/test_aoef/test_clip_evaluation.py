"""Test suite for AOEF Clip Evaluation Adapter."""

from soundevent import data
from soundevent.io.aoef.clip_evaluation import (
    ClipEvaluationAdapter,
    ClipEvaluationObject,
)


def test_clip_evaluation_can_be_converted_to_aoef(
    clip_evaluation: data.ClipEvaluation,
    clip_evaluation_adapter: ClipEvaluationAdapter,
):
    """Test that a clip evaluation can be converted to AOEF."""
    aoef = clip_evaluation_adapter.to_aoef(clip_evaluation)
    assert isinstance(aoef, ClipEvaluationObject)


def test_clip_evaluation_is_recovered(
    clip_evaluation: data.ClipEvaluation,
    clip_evaluation_adapter: ClipEvaluationAdapter,
):
    """Test that a clip evaluation is recovered."""
    aoef = clip_evaluation_adapter.to_aoef(clip_evaluation)
    recovered = clip_evaluation_adapter.to_soundevent(aoef)
    assert clip_evaluation == recovered
