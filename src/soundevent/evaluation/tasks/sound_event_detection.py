"""Sound event detection evaluation."""

from typing import (
    Callable,
    Generic,
    Iterator,
    Protocol,
    Sequence,
    Tuple,
)

import numpy as np

from soundevent import data, terms
from soundevent.evaluation import metrics
from soundevent.evaluation.encoding import (
    Encoder,
    classification_encoding,
    create_tag_encoder,
    prediction_encoding,
)
from soundevent.evaluation.match import (
    Detection,
    Match,
    match_detections_and_gts,
    match_geometries,
)
from soundevent.evaluation.tasks.common import iterate_over_valid_clips

__all__ = [
    "sound_event_detection",
    "evaluate_clip",
    "evaluate_sound_event_detection",
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


class ClipPrediction(Protocol, Generic[Detection]):
    """Protocol defining the requirements for a clip prediction object."""

    clip: data.Clip
    detections: Sequence[Detection]


def evaluate_sound_event_detection(
    clip_predictions: Sequence[ClipPrediction[Detection]],
    clip_annotations: Sequence[data.ClipAnnotation],
    affinity: Callable[[Detection, data.SoundEventAnnotation], float],
    score: Callable[[Detection], float] | None = None,
    affinity_threshold: float = 0,
    strict_match: bool = False,
) -> Iterator[
    Tuple[
        data.Clip,
        Match[Detection, data.SoundEventAnnotation],
    ]
]:
    """Evaluate sound event detections against ground truth annotations.

    This function matches predictions to annotations for each clip
    individually.

    Parameters
    ----------
    clip_predictions
        A sequence of prediction objects. Each object must contain a reference
        to the clip and a sequence of detections.
    clip_annotations
        A sequence of ground truth annotations corresponding to the same clips.
    affinity
        A function that computes the affinity score (e.g., IoU) between a
        detection and a ground truth annotation.
    score
        A function to extract the confidence score from a detection. Used to
        sort detections greedily. If None, detections are processed in the
        order provided.
    affinity_threshold
        The minimum affinity score required for a valid match. Matches with
        scores less than or equal to this value are discarded. Defaults to 0.0.
    strict_match
        If True, a detection is only matched if its highest affinity target
        is available. If False (default), it falls back to the next best
        available target.

    Yields
    ------
    clip : data.Clip
        The clip associated with the match.
    match : Match[Detection, data.SoundEventAnnotation]
        A named tuple containing the matching results, see [`Match`][Match].

    Raises
    ------
    ValueError
        If the number of predictions and annotations differs, or if the sets of
        clip UUIDs do not match exactly.
    """
    if len(clip_predictions) != len(clip_annotations):
        raise ValueError(
            "The number of clip predictions and annotations must match. "
            f"Got {len(clip_predictions)} predictions and "
            f"{len(clip_annotations)} annotations."
        )

    pred_mapping = {pred.clip.uuid: pred for pred in clip_predictions}
    ann_mapping = {ann.clip.uuid: ann for ann in clip_annotations}

    if set(pred_mapping.keys()) != set(ann_mapping.keys()):
        missing_in_pred = set(ann_mapping.keys()) - set(pred_mapping.keys())
        missing_in_ann = set(pred_mapping.keys()) - set(ann_mapping.keys())
        raise ValueError(
            "The clip predictions and annotations must be mapped to the same "
            "clips. "
            f"Missing in predictions: {missing_in_pred}. "
            f"Missing in annotations: {missing_in_ann}."
        )

    clip_uuids = set(pred_mapping.keys())

    for uuid in clip_uuids:
        clip_prediction = pred_mapping[uuid]
        clip_annotation = ann_mapping[uuid]
        clip = clip_prediction.clip
        for match in match_detections_and_gts(
            detections=clip_prediction.detections,
            ground_truths=clip_annotation.sound_events,
            affinity_threshold=affinity_threshold,
            affinity=affinity,
            score=score,
            strict_match=strict_match,
        ):
            yield clip, match


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
) -> tuple[list[int | None], list[np.ndarray], data.ClipEvaluation]:
    true_classes: list[int | None] = []
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
) -> tuple[int | None, np.ndarray, data.Match]:
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
    scores: Sequence[float | None],
) -> float:
    valid_scores = [score for score in scores if score is not None]

    if not valid_scores:
        return 0.0

    score = float(np.mean(valid_scores))
    if np.isnan(score):
        return 0.0

    return score
