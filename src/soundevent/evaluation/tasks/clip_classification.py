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
from soundevent.evaluation.tasks.common import iterate_over_valid_clips
from soundevent.terms import metrics as terms

__all__ = [
    "clip_classification",
]

EXAMPLE_METRICS = (
    (terms.true_class_probability, metrics.true_class_probability),
)

RUN_METRICS = (
    (terms.balanced_accuracy, metrics.balanced_accuracy),
    (terms.accuracy, metrics.accuracy),
    (terms.top_3_accuracy, metrics.top_3_accuracy),
)


def clip_classification(
    clip_predictions: Sequence[data.ClipPrediction],
    clip_annotations: Sequence[data.ClipAnnotation],
    tags: Sequence[data.Tag],
) -> data.Evaluation:
    # TODO: Add docstring
    encoder = create_tag_encoder(tags)

    (
        evaluated_examples,
        true_classes,
        predicted_classes_scores,
    ) = _evaluate_all_clips(clip_predictions, clip_annotations, encoder)

    evaluation_metrics = _compute_overall_metrics(
        true_classes,
        predicted_classes_scores,
    )

    score = _compute_overall_score(evaluated_examples)

    return data.Evaluation(
        evaluation_task="clip_classification",
        clip_evaluations=evaluated_examples,
        metrics=evaluation_metrics,
        score=score,
    )


def _evaluate_all_clips(
    clip_predictions: Sequence[data.ClipPrediction],
    clip_annotations: Sequence[data.ClipAnnotation],
    encoder: Encoder,
):
    """Evaluate all examples in the given prediction set."""
    evaluated_examples = []
    true_classes = []
    predicted_classes_scores = []

    for annotations, predictions in iterate_over_valid_clips(
        clip_predictions=clip_predictions,
        clip_annotations=clip_annotations,
    ):
        (
            true_class,
            predicted_class_scores,
            evaluated_example,
        ) = _evaluate_example(
            clip_annotations=annotations,
            clip_predictions=predictions,
            encoder=encoder,
            metrics=EXAMPLE_METRICS,
            scoring_fn=metrics.classification_score,
        )

        evaluated_examples.append(evaluated_example)
        true_classes.append(true_class)
        predicted_classes_scores.append(predicted_class_scores)

    return evaluated_examples, true_classes, np.array(predicted_classes_scores)


def _compute_overall_metrics(true_classes, predicted_classes_scores):
    """Compute evaluation metrics based on true classes and predicted scores."""
    evaluation_metrics = [
        data.Feature(
            term=term,
            value=metric(
                y_true=true_classes,
                y_score=predicted_classes_scores,
            ),
        )
        for term, metric in RUN_METRICS
    ]
    return evaluation_metrics


def _evaluate_example(
    clip_annotations: data.ClipAnnotation,
    clip_predictions: data.ClipPrediction,
    encoder: Encoder,
    metrics: Sequence[tuple[data.Term, metrics.Metric]],
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
        tags=clip_annotations.tags,
        encoder=encoder,
    )
    predicted_class_scores = prediction_encoding(
        tags=clip_predictions.tags,
        encoder=encoder,
    )
    evaluated = data.ClipEvaluation(
        annotations=clip_annotations,
        predictions=clip_predictions,
        metrics=[
            data.Feature(
                term=term,
                value=metric(true_class, predicted_class_scores),
            )
            for term, metric in metrics
        ],
        score=scoring_fn(true_class, predicted_class_scores),
    )
    return true_class, predicted_class_scores, evaluated


def _compute_overall_score(
    evaluated_examples: Sequence[data.ClipEvaluation],
) -> float:
    non_none_scores = [
        example.score
        for example in evaluated_examples
        if example.score is not None
    ]
    return float(np.mean(non_none_scores)) if non_none_scores else 0.0
