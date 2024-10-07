"""Test suite for sound event detection evaluation."""

from pathlib import Path

from soundevent import data, io, terms
from soundevent.evaluation import sound_event_detection

TEST_DATA = Path(__file__).parent.parent / "data"


def test_can_evaluate_nips_data():
    """Test that we can evaluate the NIPS data."""
    evaluation_set = io.load(
        TEST_DATA / "nips4b_evaluation_set.json",
        type="evaluation_set",
    )
    model_run = io.load(
        TEST_DATA / "nips4b_model_run.json",
        type="model_run",
    )

    evaluation = sound_event_detection(
        model_run.clip_predictions,
        evaluation_set.clip_annotations,
        tags=evaluation_set.evaluation_tags,
    )

    assert isinstance(evaluation, data.Evaluation)

    # check that all clips have been evaluated
    assert len(evaluation.clip_evaluations) == len(
        evaluation_set.clip_annotations
    )

    # check that all metrics are present
    assert len(evaluation.metrics) == 4
    metric_names = {metric.term for metric in evaluation.metrics}
    assert metric_names == {
        terms.balanced_accuracy,
        terms.accuracy,
        terms.top_3_accuracy,
        terms.mean_average_precision,
    }


def test_can_evaluate_example_whombat_data():
    evaluation_set = io.load(
        TEST_DATA / "example_evaluation_set.json",
        type="evaluation_set",
    )
    model_run = io.load(
        TEST_DATA / "example_model_run.json",
        type="model_run",
    )

    evaluation = sound_event_detection(
        model_run.clip_predictions,
        evaluation_set.clip_annotations,
        tags=evaluation_set.evaluation_tags,
    )

    assert isinstance(evaluation, data.Evaluation)

    # check that all clips have been evaluated
    assert len(evaluation.clip_evaluations) == len(
        evaluation_set.clip_annotations
    )

    # check that all metrics are present
    assert len(evaluation.metrics) == 4
    metric_names = {metric.term for metric in evaluation.metrics}
    assert metric_names == {
        terms.balanced_accuracy,
        terms.accuracy,
        terms.top_3_accuracy,
        terms.mean_average_precision,
    }
