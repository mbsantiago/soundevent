"""Sound event classification evaluation."""

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
from soundevent.evaluation.tasks.common import iterate_over_valid_clips
from soundevent.terms import metrics as terms

__all__ = [
    "sound_event_classification",
]

SOUNDEVENT_METRICS: Sequence[tuple[data.Term, metrics.Metric]] = (
    (terms.true_class_probability, metrics.true_class_probability),
)

EXAMPLE_METRICS: Sequence[tuple[data.Term, metrics.Metric]] = ()

RUN_METRICS: Sequence[tuple[data.Term, metrics.Metric]] = (
    (terms.balanced_accuracy, metrics.balanced_accuracy),
    (terms.balanced_accuracy, metrics.accuracy),
    (terms.balanced_accuracy, metrics.top_3_accuracy),
)


def sound_event_classification(
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
        evaluation_task="sound_event_classification",
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
        clip_predictions=clip_predictions,
        clip_annotations=clip_annotations,
    ):
        true_class, predicted_classes, evaluated_clip = _evaluate_clip(
            clip_annotations=annotations,
            clip_predictions=predictions,
            encoder=encoder,
        )

        true_classes.extend(true_class)
        predicted_classes_scores.extend(predicted_classes)
        evaluated_clips.append(evaluated_clip)

    return evaluated_clips, true_classes, np.array(predicted_classes_scores)


def _compute_overall_metrics(true_classes, predicted_classes_scores):
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


def _evaluate_clip(
    clip_annotations: data.ClipAnnotation,
    clip_predictions: data.ClipPrediction,
    encoder: Encoder,
) -> Tuple[List[Optional[int]], List[np.ndarray], data.ClipEvaluation]:
    true_classes: List[Optional[int]] = []
    predicted_classes_scores: List[np.ndarray] = []
    matches: List[data.Match] = []

    _valid_sound_events = {
        annotation.sound_event.uuid: annotation
        for annotation in clip_annotations.sound_events
    }

    for sound_event_prediction in clip_predictions.sound_events:
        if sound_event_prediction.sound_event.uuid not in _valid_sound_events:
            continue

        annotation = _valid_sound_events[
            sound_event_prediction.sound_event.uuid
        ]
        true_class, predicted_classes, match = _evaluate_sound_event(
            sound_event_prediction=sound_event_prediction,
            sound_event_annotation=annotation,
            encoder=encoder,
        )

        true_classes.append(true_class)
        predicted_classes_scores.append(predicted_classes)
        matches.append(match)

    score = np.mean(
        [match.score for match in matches if match.score is not None]
    )

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
            score=score,  # type: ignore
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
                term=term,
                value=metric(true_class, predicted_class_scores),
            )
            for term, metric in SOUNDEVENT_METRICS
        ],
    )
    return true_class, predicted_class_scores, match


def _compute_overall_score(
    evaluated_clip: Sequence[data.ClipEvaluation],
) -> float:
    non_none_scores = [
        example.score
        for example in evaluated_clip
        if example.score is not None
    ]
    return float(np.mean(non_none_scores)) if non_none_scores else 0.0
