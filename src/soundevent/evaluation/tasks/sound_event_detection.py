"""Sound event detection evaluation."""

from typing import Optional, Sequence

import numpy as np

from soundevent import data
from soundevent.evaluation import metrics
from soundevent.evaluation.encoding import (
    Encoder,
    classification_encoding,
    create_tag_encoder,
    prediction_encoding,
)
from soundevent.evaluation.match import match_geometries
from soundevent.evaluation.tasks.common import iterate_over_valid_clips
from soundevent.terms import metrics as terms

__all__ = [
    "sound_event_detection",
    "evaluate_clip",
]

SOUNDEVENT_METRICS: Sequence[tuple[data.Term, metrics.Metric]] = (
    (
        terms.true_class_probability,
        metrics.true_class_probability,
    ),
)

EXAMPLE_METRICS: Sequence[tuple[data.Term, metrics.Metric]] = ()

RUN_METRICS: Sequence[tuple[data.Term, metrics.Metric]] = (
    (terms.mean_average_precision, metrics.mean_average_precision),
    (terms.balanced_accuracy, metrics.balanced_accuracy),
    (terms.accuracy, metrics.accuracy),
    (terms.top_3_accuracy, metrics.top_3_accuracy),
)


def sound_event_detection(
    clip_predictions: Sequence[data.ClipPrediction],
    clip_annotations: Sequence[data.ClipAnnotation],
    tags: Sequence[data.Tag],
) -> data.Evaluation:
    encoder = create_tag_encoder(tags)

    (
        evaluated_clips,
        true_classes,
        predicted_classes_scores,
    ) = _evaluate_clips(clip_predictions, clip_annotations, encoder)

    evaluation_metrics = compute_overall_metrics(
        true_classes,
        predicted_classes_scores,
    )

    return data.Evaluation(
        evaluation_task="sound_event_detection",
        clip_evaluations=evaluated_clips,
        metrics=evaluation_metrics,
        score=_mean([c.score for c in evaluated_clips]),
    )


def _evaluate_clips(
    clip_predictions: Sequence[data.ClipPrediction],
    clip_annotations: Sequence[data.ClipAnnotation],
    encoder: Encoder,
):
    """Evaluate all examples in the given model run and evaluation set."""
    evaluated_clips = []
    true_classes = []
    predicted_classes_scores = []

    for annotations, predictions in iterate_over_valid_clips(
        clip_predictions=clip_predictions,
        clip_annotations=clip_annotations,
    ):
        true_class, predicted_classes, evaluated_clip = evaluate_clip(
            clip_annotations=annotations,
            clip_predictions=predictions,
            encoder=encoder,
        )

        true_classes.extend(true_class)
        predicted_classes_scores.extend(predicted_classes)
        evaluated_clips.append(evaluated_clip)

    return evaluated_clips, true_classes, np.array(predicted_classes_scores)


def compute_overall_metrics(true_classes, predicted_classes_scores):
    """Compute evaluation metrics based on true classes and predicted scores."""
    evaluation_metrics = [
        data.Feature(
            term=term,
            value=metric(
                true_classes,
                predicted_classes_scores,
            ),
        )
        for term, metric in RUN_METRICS
    ]
    return evaluation_metrics


def evaluate_clip(
    clip_annotations: data.ClipAnnotation,
    clip_predictions: data.ClipPrediction,
    encoder: Encoder,
) -> tuple[list[Optional[int]], list[np.ndarray], data.ClipEvaluation]:
    true_classes: list[Optional[int]] = []
    predicted_classes_scores: list[np.ndarray] = []
    matches: list[data.Match] = []

    # Iterate over all matches between predictions and annotations.
    for prediction_index, annotation_index, affinity in match_geometries(
        source=[
            prediction.sound_event.geometry
            for prediction in clip_predictions.sound_events
            if prediction.sound_event.geometry
        ],
        target=[
            annotation.sound_event.geometry
            for annotation in clip_annotations.sound_events
            if annotation.sound_event.geometry
        ],
    ):
        # Handle the case where a prediction was not matched
        if annotation_index is None and prediction_index is not None:
            prediction = clip_predictions.sound_events[prediction_index]
            y_score = prediction_encoding(
                tags=prediction.tags,
                encoder=encoder,
            )
            matches.append(
                data.Match(
                    source=prediction,
                    target=None,
                    affinity=affinity,
                    score=0,
                )
            )
            true_classes.append(None)
            predicted_classes_scores.append(y_score)
            continue

        # Handle the case where an annotation was not matched
        if annotation_index is not None and prediction_index is None:
            annotation = clip_annotations.sound_events[annotation_index]
            y_true = classification_encoding(
                tags=annotation.tags,
                encoder=encoder,
            )
            y_score = prediction_encoding(
                tags=[],
                encoder=encoder,
            )
            matches.append(
                data.Match(
                    source=None,
                    target=annotation,
                    affinity=affinity,
                    score=0,
                )
            )
            true_classes.append(y_true)
            predicted_classes_scores.append(y_score)
            continue

        if annotation_index is not None and prediction_index is not None:
            prediction = clip_predictions.sound_events[prediction_index]
            annotation = clip_annotations.sound_events[annotation_index]
            true_class, predicted_class_scores, match = evaluate_sound_event(
                sound_event_prediction=prediction,
                sound_event_annotation=annotation,
                encoder=encoder,
            )
            matches.append(match)
            true_classes.append(true_class)
            predicted_classes_scores.append(predicted_class_scores)
            continue

    return (
        true_classes,
        predicted_classes_scores,
        data.ClipEvaluation(
            annotations=clip_annotations,
            predictions=clip_predictions,
            metrics=[
                data.Feature(
                    term=term,
                    value=metric(
                        true_classes,
                        np.stack(predicted_classes_scores),
                    ),
                )
                for term, metric in EXAMPLE_METRICS
            ],
            score=_mean([m.score for m in matches]),
            matches=matches,
        ),
    )


def evaluate_sound_event(
    sound_event_prediction: data.SoundEventPrediction,
    sound_event_annotation: data.SoundEventAnnotation,
    encoder: Encoder,
) -> tuple[Optional[int], np.ndarray, data.Match]:
    true_class = classification_encoding(
        tags=sound_event_annotation.tags,
        encoder=encoder,
    )
    predicted_class_scores = prediction_encoding(
        tags=sound_event_prediction.tags,
        encoder=encoder,
    )
    score = metrics.classification_score(true_class, predicted_class_scores)
    match = data.Match(
        source=sound_event_prediction,
        target=sound_event_annotation,
        affinity=1,
        score=score,
        metrics=[
            data.Feature(
                term=term,
                value=metric(true_class, predicted_class_scores),
            )
            for term, metric in SOUNDEVENT_METRICS
        ],
    )
    return true_class, predicted_class_scores, match


def _mean(
    scores: Sequence[Optional[float]],
) -> float:
    valid_scores = [score for score in scores if score is not None]

    if not valid_scores:
        return 0.0

    score = float(np.mean(valid_scores))
    if np.isnan(score):
        return 0.0

    return score
