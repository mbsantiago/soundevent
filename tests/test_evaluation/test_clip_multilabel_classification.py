"""Test suite of the Clip Multi-Label Classification module."""


from typing import List

import pytest

from soundevent import data
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
def evaluation_set(
    clips: List[data.Clip],
    tags: List[data.Tag],
) -> data.EvaluationSet:
    """Create evaluation set for testing."""
    clip1, clip2, clip3 = clips
    return data.EvaluationSet(
        name="test",
        description="Test evaluation set",
        task=data.EvaluationTask.CLIP_MULTILABEL_CLASSIFICATION,
        examples=[
            data.EvaluationExample(clip=clip1, tags=[tags[0], tags[2]]),
            data.EvaluationExample(clip=clip2, tags=[tags[3]]),
            data.EvaluationExample(
                clip=clip3, tags=[tags[0], tags[1], tags[5]]
            ),
        ],
        tags=[tags[0], tags[1], tags[2]],
    )


@pytest.fixture
def model_run(
    clips: List[data.Clip],
    tags: List[data.Tag],
) -> data.ModelRun:
    """Create model run for testing."""
    clip1, clip2, _ = clips
    return data.ModelRun(
        model="test model",
        clips=[
            data.ProcessedClip(
                clip=clip1,
                tags=[
                    data.PredictedTag(tag=tags[0], score=0.9),
                    data.PredictedTag(tag=tags[2], score=0.1),
                ],
            ),
            data.ProcessedClip(
                clip=clip2,
                tags=[
                    data.PredictedTag(tag=tags[1], score=0.9),
                    data.PredictedTag(tag=tags[4], score=0.1),
                ],
            ),
        ],
    )


def test_evaluate_multilabel_fails_if_not_correct_task():
    """Test if the evaluation fails if the task is not clip multilabel
    classification."""
    with pytest.raises(ValueError):
        clip_multilabel_classification(
            model_run=data.ModelRun(model="test model", clips=[]),
            evaluation_set=data.EvaluationSet(
                name="test",
                description="Test evaluation set",
                task=data.EvaluationTask.CLIP_CLASSIFICATION,
                examples=[],
                tags=[],
            ),
        )


def test_evaluation_has_correct_model_run(evaluation_set, model_run):
    """Test if the evaluation has the correct model run."""
    evaluation = clip_multilabel_classification(
        model_run=model_run,
        evaluation_set=evaluation_set,
    )
    assert evaluation.model_run == model_run


def test_evaluation_has_correct_evaluation_set(evaluation_set, model_run):
    """Test if the evaluation has the correct evaluation set."""
    evaluation = clip_multilabel_classification(
        model_run=model_run,
        evaluation_set=evaluation_set,
    )
    assert evaluation.evaluation_set == evaluation_set


def test_evaluation_has_all_possible_evaluated_examples(
    evaluation_set, model_run
):
    """Test if the evaluation has all possible evaluated examples."""
    evaluation = clip_multilabel_classification(
        model_run=model_run,
        evaluation_set=evaluation_set,
    )
    assert len(evaluation.evaluated_examples) == 2


def test_each_evaluated_example_has_a_score(evaluation_set, model_run):
    """Test if each evaluated example has a score."""
    evaluation = clip_multilabel_classification(
        model_run=model_run,
        evaluation_set=evaluation_set,
    )
    for example in evaluation.evaluated_examples:
        assert example.score is not None


def test_each_evaluated_example_has_jaccard_metric(evaluation_set, model_run):
    """Test if each evaluated example has a jaccard metric."""
    evaluation = clip_multilabel_classification(
        model_run=model_run,
        evaluation_set=evaluation_set,
    )
    for example in evaluation.evaluated_examples:
        metric = data.find_feature(example.metrics, "jaccard")
        assert metric is not None


def test_each_evaluated_example_has_average_precision(
    evaluation_set,
    model_run,
):
    """Test if each evaluated example has an average precision metric."""
    evaluation = clip_multilabel_classification(
        model_run=model_run,
        evaluation_set=evaluation_set,
    )
    for example in evaluation.evaluated_examples:
        metric = data.find_feature(example.metrics, "average_precision")
        assert metric is not None


def test_evaluation_has_global_score(
    evaluation_set,
    model_run,
):
    """Test if the evaluation has a global score."""
    evaluation = clip_multilabel_classification(
        model_run=model_run,
        evaluation_set=evaluation_set,
    )
    assert evaluation.score is not None


def test_evaluation_has_global_mean_average_precision(
    evaluation_set,
    model_run,
):
    """Test if the evaluation has a global mean average precision."""
    evaluation = clip_multilabel_classification(
        model_run=model_run,
        evaluation_set=evaluation_set,
    )
    metric = data.find_feature(evaluation.metrics, "mean_average_precision")
    assert metric is not None
