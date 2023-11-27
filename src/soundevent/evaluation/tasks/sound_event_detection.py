"""Sound event detection evaluation."""
from typing import List, Optional, Sequence, Tuple

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

__all__ = [
    "sound_event_detection",
]

SOUNDEVENT_METRICS: Sequence[metrics.Metric] = (
    metrics.true_class_probability,
)

EXAMPLE_METRICS: Sequence[metrics.Metric] = ()

RUN_METRICS: Sequence[metrics.Metric] = (
    metrics.balanced_accuracy,
    metrics.accuracy,
    metrics.top_3_accuracy,
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

    evaluation_metrics = _compute_overall_metrics(
        true_classes,
        predicted_classes_scores,
    )

    score = _compute_overall_score(evaluated_clips)

    return data.Evaluation(
        evaluation_task="sound_event_detection",
        clip_evaluations=evaluated_clips,
        metrics=evaluation_metrics,
        score=score,
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
        clip_predictions=clip_predictions, clip_annotations=clip_annotations
    ):
        true_class, predicted_classes, evaluated_example = _evaluate_clip(
            clip_annotations=annotations,
            clip_predictions=predictions,
            encoder=encoder,
        )

        true_classes.extend(true_class)
        predicted_classes_scores.extend(predicted_classes)
        evaluated_clips.append(evaluated_example)

    return evaluated_clips, true_classes, np.array(predicted_classes_scores)


def _compute_overall_metrics(true_classes, predicted_classes_scores):
    """Compute evaluation metrics based on true classes and predicted
    scores."""
    evaluation_metrics = [
        data.Feature(
            name=metric.__name__,
            value=metric(
                true_classes,
                predicted_classes_scores,
            ),
        )
        for metric in RUN_METRICS
    ]
    return evaluation_metrics


def _evaluate_clip(
    clip_annotations: data.ClipAnnotation,
    clip_predictions: data.ClipPrediction,
    encoder: Encoder,
) -> Tuple[List[Optional[int]], List[np.ndarray], data.ClipEvaluation]:
    true_classes: List[Optional[int]] = []
    predicted_classes_scores: List[np.ndarray] = []
    matches: List[data.Match] = []

    # Iterate over all matches between predictions and annotations.
    for annotation_index, prediction_index, affinity in match_geometries(
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
            true_class, predicted_class_scores, match = _evaluate_sound_event(
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
                    name=metric.__name__,
                    value=metric(
                        true_classes,
                        np.stack(predicted_classes_scores),
                    ),
                )
                for metric in EXAMPLE_METRICS
            ],
            score=np.mean(  # type: ignore
                [match.score for match in matches if match.score],
            ),
            matches=matches,
        ),
    )


def _evaluate_sound_event(
    sound_event_prediction: data.SoundEventPrediction,
    sound_event_annotation: data.SoundEventAnnotation,
    encoder: Encoder,
) -> Tuple[Optional[int], np.ndarray, data.Match]:
    true_class = classification_encoding(
        tags=sound_event_annotation.tags,
        encoder=encoder,
    )
    predicted_class_scores = prediction_encoding(
        tags=sound_event_prediction.tags,
        encoder=encoder,
    )
    match = data.Match(
        source=sound_event_prediction,
        target=sound_event_annotation,
        affinity=1,
        score=metrics.classification_score(true_class, predicted_class_scores),
        metrics=[
            data.Feature(
                name=metric.__name__,
                value=metric(true_class, predicted_class_scores),
            )
            for metric in SOUNDEVENT_METRICS
        ],
    )
    return true_class, predicted_class_scores, match


def _compute_overall_score(
    evaluated_examples: Sequence[data.ClipEvaluation],
) -> float:
    non_none_scores = [
        example.score
        for example in evaluated_examples
        if example.score is not None
    ]
    return float(np.mean(non_none_scores)) if non_none_scores else 0.0
