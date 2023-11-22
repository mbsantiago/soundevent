"""Test suite of the Clip Classification Evaluation."""

import math
from typing import List

import pytest

from soundevent import data
from soundevent.evaluation import clip_classification


@pytest.fixture
def example_tags(random_tags) -> List[data.Tag]:
    """Tags for testing."""
    return random_tags(3)


@pytest.fixture
def example_clips(random_clips) -> List[data.Clip]:
    """Clips for testing."""
    return random_clips(3)


@pytest.fixture
def evaluation_set(
    example_clips: List[data.Clip],
    example_tags: List[data.Tag],
) -> data.EvaluationSet:
    """Create evaluation set for testing."""
    clip1, clip2, clip3 = example_clips
    tag1, tag2, tag3 = example_tags
    return data.EvaluationSet(
        name="test",
        description="Test evaluation set",
        task=data.EvaluationTask.CLIP_CLASSIFICATION,
        examples=[
            data.EvaluationExample(clip=clip1, tags=[tag1]),
            data.EvaluationExample(clip=clip2, tags=[tag2]),
            data.EvaluationExample(clip=clip3, tags=[tag3]),
        ],
        tags=[tag1, tag2, tag3],
    )


@pytest.fixture
def model_run(
    example_clips: List[data.Clip],
    example_tags: List[data.Tag],
) -> data.ModelRun:
    """Create model run for testing."""
    clip1, clip2, _ = example_clips
    tag1, tag2, _ = example_tags
    return data.ModelRun(
        model="test model",
        clips=[
            data.ProcessedClip(
                clip=clip1,
                tags=[
                    data.PredictedTag(tag=tag1, score=0.9),
                    data.PredictedTag(tag=tag2, score=0.1),
                ],
            ),
            data.ProcessedClip(
                clip=clip2,
                tags=[
                    data.PredictedTag(tag=tag1, score=0.9),
                    data.PredictedTag(tag=tag2, score=0.1),
                ],
            ),
        ],
    )


def test_evaluation_fails_if_evaluation_set_is_not_of_the_correct_type():
    evaluation_set = data.EvaluationSet(
        name="test",
        description="Test evaluation set",
        task=data.EvaluationTask.SOUND_EVENT_DETECTION,
    )
    model_run = data.ModelRun(model="test model")

    with pytest.raises(ValueError):
        clip_classification(
            evaluation_set=evaluation_set,
            model_run=model_run,
        )


def test_evaluation_returns_an_evaluation_object(
    evaluation_set: data.EvaluationSet,
    model_run: data.ModelRun,
):
    """Test that the evaluation returns an evaluation object."""
    evaluation = clip_classification(
        evaluation_set=evaluation_set,
        model_run=model_run,
    )

    assert isinstance(evaluation, data.Evaluation)


def test_all_possible_clips_were_evaluated(
    evaluation_set: data.EvaluationSet,
    model_run: data.ModelRun,
):
    """Test that all possible clips were evaluated."""
    evaluation = clip_classification(
        evaluation_set=evaluation_set,
        model_run=model_run,
    )

    assert len(evaluation.evaluated_examples) == 2


def test_evaluated_examples_contain_true_class_probability(
    evaluation_set: data.EvaluationSet,
    model_run: data.ModelRun,
):
    evaluation = clip_classification(
        evaluation_set=evaluation_set,
        model_run=model_run,
    )

    true_class_prob_0 = data.find_feature(
        evaluation.evaluated_examples[0].metrics, name="true_class_probability"
    )
    assert true_class_prob_0 is not None
    assert math.isclose(true_class_prob_0.value, 0.9, rel_tol=1e-6)

    true_class_prob_1 = data.find_feature(
        evaluation.evaluated_examples[1].metrics, name="true_class_probability"
    )
    assert true_class_prob_1 is not None
    assert math.isclose(true_class_prob_1.value, 0.1, rel_tol=1e-6)


def test_evaluation_has_accuracy(
    evaluation_set: data.EvaluationSet,
    model_run: data.ModelRun,
):
    """Test that the evaluation has an accuracy."""
    evaluation = clip_classification(
        evaluation_set=evaluation_set,
        model_run=model_run,
    )

    accuracy = data.find_feature(evaluation.metrics, name="accuracy")
    assert accuracy is not None
    assert math.isclose(accuracy.value, 0.5, rel_tol=1e-6)


def test_evaluation_has_balanced_accuracy(
    evaluation_set: data.EvaluationSet,
    model_run: data.ModelRun,
):
    """Test that the evaluation has a balanced accuracy."""
    evaluation = clip_classification(
        evaluation_set=evaluation_set,
        model_run=model_run,
    )

    balanced_accuracy = data.find_feature(
        evaluation.metrics, name="balanced_accuracy"
    )
    assert balanced_accuracy is not None
    assert math.isclose(balanced_accuracy.value, 0.5, rel_tol=1e-6)


def test_evaluation_has_top_3_accuracy(
    evaluation_set: data.EvaluationSet,
    model_run: data.ModelRun,
):
    """Test that the evaluation has a top 3 accuracy."""
    evaluation = clip_classification(
        evaluation_set=evaluation_set,
        model_run=model_run,
    )

    top_3_accuracy = data.find_feature(
        evaluation.metrics, name="top_3_accuracy"
    )
    assert top_3_accuracy is not None
    assert math.isclose(top_3_accuracy.value, 1.0, rel_tol=1e-6)


def test_evaluation_with_missing_class(
    example_clips: List[data.Clip],
    example_tags: List[data.Tag],
    model_run: data.ModelRun,
):
    """Test that the evaluation works with missing classes."""
    clip1, clip2, _ = example_clips
    tag1, tag2, tag3 = example_tags
    evaluation_set = data.EvaluationSet(
        name="test",
        description="Test evaluation set",
        task=data.EvaluationTask.CLIP_CLASSIFICATION,
        examples=[
            data.EvaluationExample(clip=clip1, tags=[tag1]),
            data.EvaluationExample(clip=clip2, tags=[tag3]),
        ],
        tags=[tag1, tag2],
    )

    evaluation = clip_classification(
        evaluation_set=evaluation_set,
        model_run=model_run,
    )

    assert len(evaluation.evaluated_examples) == 2
    assert len(evaluation.metrics) == 3
    assert len(evaluation.evaluated_examples[0].metrics) == 1
    assert len(evaluation.evaluated_examples[1].metrics) == 1


def test_overall_score_is_the_mean_of_the_scores_of_all_evaluated_examples(
    evaluation_set: data.EvaluationSet,
    model_run: data.ModelRun,
):
    """Test that the overall score is the mean of the scores of all evaluated
    examples."""
    evaluation = clip_classification(
        evaluation_set=evaluation_set,
        model_run=model_run,
    )

    assert evaluation.score is not None
    assert math.isclose(evaluation.score, 0.5, rel_tol=1e-6)


def test_each_example_score_is_the_probability_of_the_true_class(
    evaluation_set: data.EvaluationSet,
    model_run: data.ModelRun,
):
    """Test that each example score is the probability of the true class."""
    evaluation = clip_classification(
        evaluation_set=evaluation_set,
        model_run=model_run,
    )

    assert len(evaluation.evaluated_examples) == 2
    assert len(evaluation.evaluated_examples[0].metrics) == 1
    assert len(evaluation.evaluated_examples[1].metrics) == 1

    assert evaluation.evaluated_examples[0].score is not None
    assert math.isclose(
        evaluation.evaluated_examples[0].score, 0.9, rel_tol=1e-6
    )

    assert evaluation.evaluated_examples[1].score is not None
    assert math.isclose(
        evaluation.evaluated_examples[1].score, 0.1, rel_tol=1e-6
    )