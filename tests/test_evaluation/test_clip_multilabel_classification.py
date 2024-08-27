"""Test suite of the Clip Multi-Label Classification module."""

from typing import List

import pytest

from soundevent import data, terms
from soundevent.evaluation import clip_multilabel_classification


@pytest.fixture
def tags(random_tags) -> List[data.Tag]:
    """Tags for testing."""
    return random_tags(6)


@pytest.fixture
def clips(random_clips) -> List[data.Clip]:
    """Clips for testing."""
    return random_clips(3)


@pytest.fixture
def evaluation_tags(tags: List[data.Tag]) -> List[data.Tag]:
    """Create evaluation tags for testing."""
    return tags[:3]


@pytest.fixture
def annotation_set(
    clips: List[data.Clip],
    tags: List[data.Tag],
) -> data.AnnotationSet:
    """Create evaluation set for testing."""
    clip1, clip2, clip3 = clips
    return data.AnnotationSet(
        clip_annotations=[
            data.ClipAnnotation(clip=clip1, tags=[tags[0], tags[2]]),
            data.ClipAnnotation(clip=clip2, tags=[tags[3]]),
            data.ClipAnnotation(clip=clip3, tags=[tags[0], tags[1], tags[5]]),
        ],
    )


@pytest.fixture
def prediction_set(
    clips: List[data.Clip],
    tags: List[data.Tag],
) -> data.PredictionSet:
    """Create model run for testing."""
    clip1, clip2, _ = clips
    return data.PredictionSet(
        clip_predictions=[
            data.ClipPrediction(
                clip=clip1,
                tags=[
                    data.PredictedTag(tag=tags[0], score=0.9),
                    data.PredictedTag(tag=tags[2], score=0.1),
                ],
            ),
            data.ClipPrediction(
                clip=clip2,
                tags=[
                    data.PredictedTag(tag=tags[1], score=0.9),
                    data.PredictedTag(tag=tags[4], score=0.1),
                ],
            ),
        ],
    )


def test_evaluation_has_all_possible_evaluated_examples(
    annotation_set: data.AnnotationSet,
    prediction_set: data.PredictionSet,
    evaluation_tags: List[data.Tag],
):
    """Test if the evaluation has all possible evaluated examples."""
    evaluation = clip_multilabel_classification(
        clip_predictions=prediction_set.clip_predictions,
        clip_annotations=annotation_set.clip_annotations,
        tags=evaluation_tags,
    )
    assert len(evaluation.clip_evaluations) == 2


def test_each_evaluated_example_has_a_score(
    annotation_set: data.AnnotationSet,
    prediction_set: data.PredictionSet,
    evaluation_tags: List[data.Tag],
):
    """Test if each evaluated example has a score."""
    evaluation = clip_multilabel_classification(
        clip_predictions=prediction_set.clip_predictions,
        clip_annotations=annotation_set.clip_annotations,
        tags=evaluation_tags,
    )
    for example in evaluation.clip_evaluations:
        assert example.score is not None


def test_each_evaluated_example_has_jaccard_metric(
    annotation_set: data.AnnotationSet,
    prediction_set: data.PredictionSet,
    evaluation_tags: List[data.Tag],
):
    """Test if each evaluated example has a jaccard metric."""
    evaluation = clip_multilabel_classification(
        clip_predictions=prediction_set.clip_predictions,
        clip_annotations=annotation_set.clip_annotations,
        tags=evaluation_tags,
    )
    for example in evaluation.clip_evaluations:
        metric = data.find_feature(example.metrics, term=terms.jaccard_index)
        assert metric is not None


def test_each_evaluated_example_has_average_precision(
    annotation_set: data.AnnotationSet,
    prediction_set: data.PredictionSet,
    evaluation_tags: List[data.Tag],
):
    """Test if each evaluated example has an average precision metric."""
    evaluation = clip_multilabel_classification(
        clip_predictions=prediction_set.clip_predictions,
        clip_annotations=annotation_set.clip_annotations,
        tags=evaluation_tags,
    )
    for example in evaluation.clip_evaluations:
        metric = data.find_feature(
            example.metrics, term=terms.average_precision
        )
        assert metric is not None


def test_evaluation_has_global_score(
    annotation_set: data.AnnotationSet,
    prediction_set: data.PredictionSet,
    evaluation_tags: List[data.Tag],
):
    """Test if the evaluation has a global score."""
    evaluation = clip_multilabel_classification(
        clip_predictions=prediction_set.clip_predictions,
        clip_annotations=annotation_set.clip_annotations,
        tags=evaluation_tags,
    )
    assert evaluation.score is not None


def test_evaluation_has_global_mean_average_precision(
    annotation_set: data.AnnotationSet,
    prediction_set: data.PredictionSet,
    evaluation_tags: List[data.Tag],
):
    """Test if the evaluation has a global mean average precision."""
    evaluation = clip_multilabel_classification(
        clip_predictions=prediction_set.clip_predictions,
        clip_annotations=annotation_set.clip_annotations,
        tags=evaluation_tags,
    )
    metric = data.find_feature(
        evaluation.metrics,
        term=terms.mean_average_precision,
    )
    assert metric is not None
