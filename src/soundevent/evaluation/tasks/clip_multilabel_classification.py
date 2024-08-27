from typing import List, Sequence, Tuple

import numpy as np

from soundevent import data
from soundevent.evaluation import metrics
from soundevent.evaluation.encoding import (
    Encoder,
    create_tag_encoder,
    multilabel_encoding,
    prediction_encoding,
)
from soundevent.evaluation.tasks.common import iterate_over_valid_clips
from soundevent.terms import metrics as terms

__all__ = [
    "clip_multilabel_classification",
]

EXAMPLE_METRICS: Sequence[tuple[data.Term, metrics.Metric]] = (
    (terms.jaccard_index, metrics.jaccard),
    (terms.average_precision, metrics.average_precision),
)

RUN_METRICS: Sequence[tuple[data.Term, metrics.Metric]] = (
    (terms.mean_average_precision, metrics.mean_average_precision),
)


def clip_multilabel_classification(
    clip_predictions: Sequence[data.ClipPrediction],
    clip_annotations: Sequence[data.ClipAnnotation],
    tags: Sequence[data.Tag],
) -> data.Evaluation:
    # TODO: Add docstring

    encoder = create_tag_encoder(tags)

    (
        evaluated_clips,
        true_classes,
        predicted_classes_scores,
    ) = _evaluate_clips(clip_predictions, clip_annotations, encoder)

    evaluation_metrics = _compute_overall_metrics(
        true_classes,
        predicted_classes_scores,
    )

    score = _compute_overall_score(evaluated_clips)

    return data.Evaluation(
        evaluation_task="clip_multilabel_classification",
        clip_evaluations=evaluated_clips,
        metrics=evaluation_metrics,
        score=score,
    )


def _evaluate_clips(
    clip_predictions: Sequence[data.ClipPrediction],
    clip_annotations: Sequence[data.ClipAnnotation],
    encoder: Encoder,
) -> Tuple[
    List[data.ClipEvaluation],
    np.ndarray,
    np.ndarray,
]:
    """Evaluate all examples in the given model run and evaluation set."""
    evaluated_clips = []
    true_classes = []
    predicted_classes_scores = []

    for annotations, predictions in iterate_over_valid_clips(
        clip_predictions=clip_predictions,
        clip_annotations=clip_annotations,
    ):
        (
            true_class,
            predicted_class_scores,
            evaluated_clip,
        ) = _evaluate_clip(
            clip_annotations=annotations,
            clip_predictions=predictions,
            encoder=encoder,
        )

        evaluated_clips.append(evaluated_clip)
        true_classes.append(true_class)
        predicted_classes_scores.append(predicted_class_scores)

    return (
        evaluated_clips,
        np.array(true_classes),
        np.array(predicted_classes_scores),
    )


def _compute_overall_metrics(
    true_classes,
    predicted_classes_scores,
) -> List[data.Feature]:
    """Compute evaluation metrics based on true classes and predicted scores."""
    return [
        data.Feature(
            term=term,
            value=metric(
                true_classes,
                predicted_classes_scores,
            ),
        )
        for term, metric in RUN_METRICS
    ]


def _evaluate_clip(
    clip_annotations: data.ClipAnnotation,
    clip_predictions: data.ClipPrediction,
    encoder: Encoder,
) -> Tuple[np.ndarray, np.ndarray, data.ClipEvaluation]:
    """Evaluate a single clip.

    Parameters
    ----------
    clip_annotations
        The annotations of the clip to evaluate.
    clip_predictions
        The predictions of the clip to evaluate.
    encoder
        The encoder used to encode the tags into integer encoded classes.

    Returns
    -------
    true_class
        The true class of the example.
    predicted_class_scores
        The predicted class scores of the example.
    evaluated_clip
        The evaluated example.
    """
    true_class = multilabel_encoding(
        tags=clip_annotations.tags,
        encoder=encoder,
    )
    predicted_class_scores = prediction_encoding(
        tags=clip_predictions.tags,
        encoder=encoder,
    )
    evaluated_clip = data.ClipEvaluation(
        annotations=clip_annotations,
        predictions=clip_predictions,
        metrics=[
            data.Feature(
                term=term,
                value=metric(true_class, predicted_class_scores),
            )
            for term, metric in EXAMPLE_METRICS
        ],
        score=metrics.multilabel_example_score(
            true_class,
            predicted_class_scores,
        ),
    )
    return true_class, predicted_class_scores, evaluated_clip


def _compute_overall_score(
    evaluated_examples: Sequence[data.ClipEvaluation],
) -> float:
    valid_scores = [
        example.score
        for example in evaluated_examples
        if example.score is not None
    ]
    return float(np.mean(valid_scores)) if valid_scores else 0.0
