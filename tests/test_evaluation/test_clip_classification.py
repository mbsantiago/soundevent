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
def annotation_set(
    example_clips: List[data.Clip],
    example_tags: List[data.Tag],
) -> data.AnnotationSet:
    """Create evaluation set for testing."""
    clip1, clip2, clip3 = example_clips
    tag1, tag2, tag3 = example_tags
    return data.AnnotationSet(
        clip_annotations=[
            data.ClipAnnotation(clip=clip1, tags=[tag1]),
            data.ClipAnnotation(clip=clip2, tags=[tag2]),
            data.ClipAnnotation(clip=clip3, tags=[tag3]),
        ],
    )


@pytest.fixture
def evaluation_tags(example_tags: List[data.Tag]) -> List[data.Tag]:
    """Create evaluation tags for testing."""
    tag1, tag2, tag3 = example_tags
    return [tag1, tag2, tag3]


@pytest.fixture
def prediction_set(
    example_clips: List[data.Clip],
    example_tags: List[data.Tag],
) -> data.PredictionSet:
    """Create model run for testing."""
    clip1, clip2, _ = example_clips
    tag1, tag2, _ = example_tags
    return data.PredictionSet(
        clip_predictions=[
            data.ClipPrediction(
                clip=clip1,
                tags=[
                    data.PredictedTag(tag=tag1, score=0.9),
                    data.PredictedTag(tag=tag2, score=0.1),
                ],
            ),
            data.ClipPrediction(
                clip=clip2,
                tags=[
                    data.PredictedTag(tag=tag1, score=0.9),
                    data.PredictedTag(tag=tag2, score=0.1),
                ],
            ),
        ],
    )


def test_evaluation_returns_an_evaluation_object(
    annotation_set: data.AnnotationSet,
    prediction_set: data.PredictionSet,
    evaluation_tags: List[data.Tag],
):
    """Test that the evaluation returns an evaluation object."""
    evaluation = clip_classification(
        clip_predictions=prediction_set.clip_predictions,
        clip_annotations=annotation_set.clip_annotations,
        tags=evaluation_tags,
    )

    assert isinstance(evaluation, data.Evaluation)


def test_all_possible_clips_were_evaluated(
    annotation_set: data.AnnotationSet,
    prediction_set: data.PredictionSet,
    evaluation_tags: List[data.Tag],
):
    """Test that all possible clips were evaluated."""
    evaluation = clip_classification(
        clip_predictions=prediction_set.clip_predictions,
        clip_annotations=annotation_set.clip_annotations,
        tags=evaluation_tags,
    )

    assert len(evaluation.clip_evaluations) == 2


def test_evaluated_clips_contain_true_class_probability(
    annotation_set: data.AnnotationSet,
    prediction_set: data.PredictionSet,
    evaluation_tags: List[data.Tag],
):
    evaluation = clip_classification(
        clip_predictions=prediction_set.clip_predictions,
        clip_annotations=annotation_set.clip_annotations,
        tags=evaluation_tags,
    )

    true_class_prob_0 = data.find_feature(
        evaluation.clip_evaluations[0].metrics,
        label="True Class Probability",
    )
    assert true_class_prob_0 is not None
    assert math.isclose(true_class_prob_0.value, 0.9, rel_tol=1e-6)

    true_class_prob_1 = data.find_feature(
        evaluation.clip_evaluations[1].metrics,
        label="True Class Probability",
    )
    assert true_class_prob_1 is not None
    assert math.isclose(true_class_prob_1.value, 0.1, rel_tol=1e-6)


def test_evaluation_has_accuracy(
    annotation_set: data.AnnotationSet,
    prediction_set: data.PredictionSet,
    evaluation_tags: List[data.Tag],
):
    """Test that the evaluation has an accuracy."""
    evaluation = clip_classification(
        clip_predictions=prediction_set.clip_predictions,
        clip_annotations=annotation_set.clip_annotations,
        tags=evaluation_tags,
    )

    accuracy = data.find_feature(evaluation.metrics, label="Accuracy")
    assert accuracy is not None
    assert math.isclose(accuracy.value, 0.5, rel_tol=1e-6)


def test_evaluation_has_balanced_accuracy(
    annotation_set: data.AnnotationSet,
    prediction_set: data.PredictionSet,
    evaluation_tags: List[data.Tag],
):
    """Test that the evaluation has a balanced accuracy."""
    evaluation = clip_classification(
        clip_annotations=annotation_set.clip_annotations,
        clip_predictions=prediction_set.clip_predictions,
        tags=evaluation_tags,
    )

    balanced_accuracy = data.find_feature(
        evaluation.metrics, label="Balanced Accuracy"
    )
    assert balanced_accuracy is not None
    assert math.isclose(balanced_accuracy.value, 0.5, rel_tol=1e-6)


def test_evaluation_has_top_3_accuracy(
    annotation_set: data.AnnotationSet,
    prediction_set: data.PredictionSet,
    evaluation_tags: List[data.Tag],
):
    """Test that the evaluation has a top 3 accuracy."""
    evaluation = clip_classification(
        clip_annotations=annotation_set.clip_annotations,
        clip_predictions=prediction_set.clip_predictions,
        tags=evaluation_tags,
    )

    top_3_accuracy = data.find_feature(
        evaluation.metrics, label="Top 3 Accuracy"
    )
    assert top_3_accuracy is not None
    assert math.isclose(top_3_accuracy.value, 1.0, rel_tol=1e-6)


def test_evaluation_with_missing_class(
    example_clips: List[data.Clip],
    example_tags: List[data.Tag],
    prediction_set: data.PredictionSet,
    evaluation_tags: List[data.Tag],
):
    """Test that the evaluation works with missing classes."""
    clip1, clip2, _ = example_clips
    tag1, _, tag3 = example_tags
    annotation_set = data.AnnotationSet(
        clip_annotations=[
            data.ClipAnnotation(clip=clip1, tags=[tag1]),
            data.ClipAnnotation(clip=clip2, tags=[tag3]),
        ],
    )

    evaluation = clip_classification(
        clip_annotations=annotation_set.clip_annotations,
        clip_predictions=prediction_set.clip_predictions,
        tags=evaluation_tags,
    )

    assert len(evaluation.clip_evaluations) == 2
    assert len(evaluation.metrics) == 3
    assert len(evaluation.clip_evaluations[0].metrics) == 1
    assert len(evaluation.clip_evaluations[1].metrics) == 1


def test_overall_score_is_the_mean_of_the_scores_of_all_evaluated_clips(
    annotation_set: data.AnnotationSet,
    prediction_set: data.PredictionSet,
    evaluation_tags: List[data.Tag],
):
    """Test that the overall score is the mean of the scores of all evaluated examples."""
    evaluation = clip_classification(
        clip_annotations=annotation_set.clip_annotations,
        clip_predictions=prediction_set.clip_predictions,
        tags=evaluation_tags,
    )

    assert evaluation.score is not None
    assert math.isclose(evaluation.score, 0.5, rel_tol=1e-6)


def test_each_example_score_is_the_probability_of_the_true_class(
    annotation_set: data.AnnotationSet,
    prediction_set: data.PredictionSet,
    evaluation_tags: List[data.Tag],
):
    """Test that each example score is the probability of the true class."""
    evaluation = clip_classification(
        clip_annotations=annotation_set.clip_annotations,
        clip_predictions=prediction_set.clip_predictions,
        tags=evaluation_tags,
    )

    assert len(evaluation.clip_evaluations) == 2
    assert len(evaluation.clip_evaluations[0].metrics) == 1
    assert len(evaluation.clip_evaluations[1].metrics) == 1

    assert evaluation.clip_evaluations[0].score is not None
    assert math.isclose(
        evaluation.clip_evaluations[0].score, 0.9, rel_tol=1e-6
    )

    assert evaluation.clip_evaluations[1].score is not None
    assert math.isclose(
        evaluation.clip_evaluations[1].score, 0.1, rel_tol=1e-6
    )
