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
from soundevent.evaluation.tasks.common import iterate_over_valid_examples

__all__ = [
    "sound_event_classification",
]

SOUNDEVENT_METRICS = (metrics.true_class_probability,)

EXAMPLE_METRICS = ()

RUN_METRICS = (
    metrics.balanced_accuracy,
    metrics.accuracy,
    metrics.top_3_accuracy,
)


def sound_event_classification(
    model_run: data.ModelRun,
    evaluation_set: data.EvaluationSet,
) -> data.Evaluation:
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
    if task != data.EvaluationTask.SOUND_EVENT_CLASSIFICATION:
        raise ValueError(
            f"Invalid evaluation task {task} for sound event "
            "classification evaluation"
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
        true_class, predicted_classes, evaluated_example = _evaluate_example(
            example=example,
            processed_clip=processed_clip,
            encoder=encoder,
        )

        true_classes.extend(true_class)
        predicted_classes_scores.extend(predicted_classes)
        evaluated_examples.append(evaluated_example)

    return evaluated_examples, true_classes, np.array(predicted_classes_scores)


def _compute_run_metrics(true_classes, predicted_classes_scores):
    """Compute evaluation metrics based on true classes and predicted
    scores."""
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
) -> Tuple[List[Optional[int]], List[np.ndarray], data.EvaluatedExample]:
    true_classes: List[Optional[int]] = []
    predicted_classes_scores: List[np.ndarray] = []
    matches: List[data.Match] = []

    _valid_sound_events = {
        annotation.sound_event.uuid: annotation
        for annotation in example.annotations
    }

    for predicted_sound_event in processed_clip.sound_events:
        if predicted_sound_event.sound_event.uuid not in _valid_sound_events:
            continue

        annotation = _valid_sound_events[
            predicted_sound_event.sound_event.uuid
        ]
        true_class, predicted_classes, match = _evaluate_sound_event(
            predicted_sound_event=predicted_sound_event,
            annotation=annotation,
            encoder=encoder,
        )

        true_classes.append(true_class)
        predicted_classes_scores.append(predicted_classes)
        matches.append(match)

    return (
        true_classes,
        predicted_classes_scores,
        data.EvaluatedExample(
            example=example,
            prediction=processed_clip,
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
            score=np.mean([match.score for match in matches if match.score]),
            matches=matches,
        ),
    )


def _evaluate_sound_event(
    predicted_sound_event: data.PredictedSoundEvent,
    annotation: data.Annotation,
    encoder: Encoder,
) -> Tuple[Optional[int], np.ndarray, data.Match]:
    true_class = classification_encoding(
        tags=annotation.tags,
        encoder=encoder,
    )
    predicted_class_scores = prediction_encoding(
        tags=predicted_sound_event.tags,
        encoder=encoder,
    )
    match = data.Match(
        source=predicted_sound_event,
        target=annotation,
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


def _compute_run_score(
    evaluated_examples: Sequence[data.EvaluatedExample],
) -> float:
    non_none_scores = [
        example.score
        for example in evaluated_examples
        if example.score is not None
    ]
    return float(np.mean(non_none_scores)) if non_none_scores else 0.0
