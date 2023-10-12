from typing import Sequence

import numpy as np

from soundevent import data
from soundevent.evaluation import metrics
from soundevent.evaluation.encoding import (
    Encoder,
    classification_encoding,
    create_tag_encoder,
    prediction_encoding,
)
from soundevent.evaluation.tasks.common import iterate_over_valid_examples

__all__ = [
    "clip_classification",
]

EXAMPLE_METRICS = (metrics.true_class_probability,)

RUN_METRICS = (
    metrics.balanced_accuracy,
    metrics.accuracy,
    metrics.top_3_accuracy,
)


def clip_classification(
    model_run: data.ModelRun,
    evaluation_set: data.EvaluationSet,
) -> data.Evaluation:
    """Evaluate clip classification.

    Parameters
    ----------
    model_run : data.ModelRun
        The model run to be evaluated.
    evaluation_set : data.EvaluationSet
        The evaluation set containing clips and associated tags.

    Returns
    -------
    data.Evaluation
        An object containing evaluation results, including evaluated examples
        and computed metrics.
    """
    _validate_evaluation_task(evaluation_set.task)

    encoder = create_tag_encoder(evaluation_set.tags)

    (
        evaluated_examples,
        true_classes,
        predicted_classes_scores,
    ) = _evaluate_all_examples(model_run, evaluation_set, encoder)

    evaluation_metrics = _compute_run_metrics(
        true_classes,
        predicted_classes_scores,
    )

    score = _compute_run_score(evaluated_examples)

    return data.Evaluation(
        model_run=model_run,
        evaluation_set=evaluation_set,
        evaluated_examples=evaluated_examples,
        metrics=evaluation_metrics,
        score=score,
    )


def _validate_evaluation_task(task: data.EvaluationTask):
    """Validate if the evaluation task is for clip classification."""
    if task != data.EvaluationTask.CLIP_CLASSIFICATION:
        raise ValueError(
            f"Invalid evaluation task {task} for clip classification evaluation"
        )


def _evaluate_all_examples(
    model_run: data.ModelRun,
    evaluation_set: data.EvaluationSet,
    encoder: Encoder,
):
    """Evaluate all examples in the given model run and evaluation set."""
    evaluated_examples = []
    true_classes = []
    predicted_classes_scores = []

    for example, processed_clip in iterate_over_valid_examples(
        model_run=model_run, evaluation_set=evaluation_set
    ):
        (
            true_class,
            predicted_class_scores,
            evaluated_example,
        ) = _evaluate_example(
            example=example,
            processed_clip=processed_clip,
            encoder=encoder,
            metrics=EXAMPLE_METRICS,
            scoring_fn=metrics.classification_score,
        )

        evaluated_examples.append(evaluated_example)
        true_classes.append(true_class)
        predicted_classes_scores.append(predicted_class_scores)

    return evaluated_examples, true_classes, np.array(predicted_classes_scores)


def _compute_run_metrics(true_classes, predicted_classes_scores):
    """Compute evaluation metrics based on true classes and predicted scores."""
    evaluation_metrics = [
        data.Feature(
            name=metric.__name__,
            value=metric(
                y_true=true_classes, y_score=predicted_classes_scores
            ),
        )
        for metric in RUN_METRICS
    ]
    return evaluation_metrics


def _evaluate_example(
    example: data.EvaluationExample,
    processed_clip: data.ProcessedClip,
    encoder: Encoder,
    metrics: Sequence[metrics.Metric],
    scoring_fn: metrics.Metric,
):
    """Evaluate a single example.

    Parameters
    ----------
    example
        The evaluation example to evaluate.
    processed_clip
        The clip that was processed by the model and contains the predictions
        for the evaluation example.
    encoder
        The encoder used to encode the tags into integer encoded classes.
    num_classes
        Total number of classes.
    metrics
        Sequence of metrics to use for evaluation.
    scoring_fn
        The scoring function to use for evaluation.

    Returns
    -------
    true_class
        The true class of the example.
    predicted_class_scores
        The predicted class scores of the example.
    evaluated
        The evaluated example.
    """
    true_class = classification_encoding(
        tags=example.tags,
        encoder=encoder,
    )
    predicted_class_scores = prediction_encoding(
        tags=processed_clip.tags,
        encoder=encoder,
    )
    evaluated = data.EvaluatedExample(
        example=example,
        prediction=processed_clip,
        metrics=[
            data.Feature(
                name=metric.__name__,
                value=metric(true_class, predicted_class_scores),
            )
            for metric in metrics
        ],
        score=scoring_fn(true_class, predicted_class_scores),
    )
    return true_class, predicted_class_scores, evaluated


def _compute_run_score(
    evaluated_examples: Sequence[data.EvaluatedExample],
) -> float:
    non_none_scores = [
        example.score
        for example in evaluated_examples
        if example.score is not None
    ]
    return float(np.mean(non_none_scores)) if non_none_scores else 0.0
