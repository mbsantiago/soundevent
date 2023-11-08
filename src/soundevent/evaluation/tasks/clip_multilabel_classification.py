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
from soundevent.evaluation.tasks.common import iterate_over_valid_examples

__all__ = [
    "clip_multilabel_classification",
]

EXAMPLE_METRICS: Sequence[metrics.Metric] = (
    metrics.jaccard,
    metrics.average_precision,
)

RUN_METRICS: Sequence[metrics.Metric] = (metrics.mean_average_precision,)


def clip_multilabel_classification(
    model_run: data.ModelRun,
    evaluation_set: data.EvaluationSet,
) -> data.Evaluation:
    """Evaluate clip multilabel classification.

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
    if task != data.EvaluationTask.CLIP_MULTILABEL_CLASSIFICATION:
        raise ValueError(
            f"Invalid evaluation task {task} for clip multilabel "
            "classification evaluation"
        )


def _evaluate_all_examples(
    model_run: data.ModelRun,
    evaluation_set: data.EvaluationSet,
    encoder: Encoder,
) -> Tuple[List[data.EvaluatedExample], np.ndarray, np.ndarray,]:
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
        )

        evaluated_examples.append(evaluated_example)
        true_classes.append(true_class)
        predicted_classes_scores.append(predicted_class_scores)

    return (
        evaluated_examples,
        np.array(true_classes),
        np.array(predicted_classes_scores),
    )


def _compute_run_metrics(
    true_classes, predicted_classes_scores
) -> List[data.Feature]:
    """Compute evaluation metrics based on true classes and predicted
    scores."""
    return [
        data.Feature(
            name=metric.__name__,
            value=metric(
                true_classes,
                predicted_classes_scores,
            ),
        )
        for metric in RUN_METRICS
    ]


def _evaluate_example(
    example: data.EvaluationExample,
    processed_clip: data.ProcessedClip,
    encoder: Encoder,
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

    Returns
    -------
    true_class
        The true class of the example.
    predicted_class_scores
        The predicted class scores of the example.
    evaluated
        The evaluated example.
    """
    true_class = multilabel_encoding(
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
            for metric in EXAMPLE_METRICS
        ],
        score=metrics.multilabel_example_score(
            true_class,
            predicted_class_scores,
        ),
    )
    return true_class, predicted_class_scores, evaluated


def _compute_run_score(
    evaluated_examples: Sequence[data.EvaluatedExample],
) -> float:
    valid_scores = [
        example.score
        for example in evaluated_examples
        if example.score is not None
    ]
    return float(np.mean(valid_scores)) if valid_scores else 0.0
