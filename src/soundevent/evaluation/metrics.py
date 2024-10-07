from typing import Any, Callable, Optional, Sequence

import numpy as np
from sklearn import metrics

__all__ = [
    "jaccard",
    "average_precision",
    "mean_average_precision",
    "classification_score",
    "true_class_probability",
    "balanced_accuracy",
    "accuracy",
    "top_3_accuracy",
    "Metric",
]

Metric = Callable[[Any, np.ndarray], float]


def classification_score(
    y_true: Optional[int],
    y_score: np.ndarray,
) -> float:
    if y_true is None:
        return 1 - y_score.sum()

    return y_score[y_true]


def true_class_probability(
    y_true: Optional[int],
    y_score: np.ndarray,
) -> float:
    if y_true is None:
        return 1 - y_score.sum()

    return y_score[y_true]


def balanced_accuracy(
    y_true: Sequence[Optional[int]],
    y_score: np.ndarray,
) -> float:
    num_classes = y_score.shape[1]
    y_true_array = np.array(
        [y if y is not None else num_classes for y in y_true]
    )
    y_score = np.c_[y_score, 1 - y_score.sum(axis=1, keepdims=True)]
    y_pred = y_score.argmax(axis=1)
    return metrics.balanced_accuracy_score(
        y_true=y_true_array,
        y_pred=y_pred,
    )


def accuracy(
    y_true: Sequence[Optional[int]],
    y_score: np.ndarray,
) -> float:
    num_classes = y_score.shape[1]
    y_true_array = np.array(
        [y if y is not None else num_classes for y in y_true]
    )
    y_score = np.c_[y_score, 1 - y_score.sum(axis=1, keepdims=True)]
    y_pred = y_score.argmax(axis=1)
    return metrics.accuracy_score(  # type: ignore
        y_true=y_true_array,
        y_pred=y_pred,
    )


def top_3_accuracy(
    y_true: Sequence[Optional[int]],
    y_score: np.ndarray,
) -> float:
    num_classes = y_score.shape[1]
    y_true_array = np.array(
        [y if y is not None else num_classes for y in y_true]
    )
    y_score = np.c_[y_score, 1 - y_score.sum(axis=1, keepdims=True)]
    return metrics.top_k_accuracy_score(  # type: ignore
        y_true=y_true_array,
        y_score=y_score,
        k=3,
        normalize=True,
        labels=list(range(num_classes + 1)),
    )


def multilabel_example_score(
    y_true: np.ndarray,
    y_score: np.ndarray,
) -> float:
    if y_true.ndim == 1:
        y_true = y_true[np.newaxis, :]

    if y_score.ndim == 1:
        y_score = y_score[np.newaxis, :]

    loss = metrics.log_loss(y_true, y_score, normalize=True)
    return np.exp(-loss)


def jaccard(
    y_true: np.ndarray,
    y_score: np.ndarray,
    threshold: float = 0.5,
) -> float:
    """Compute the Jaccard score for the given true and predicted labels.

    Parameters
    ----------
    y_true
        True labels.
    y_score
        An array of predicted probabilities for each class.
    threshold
        The threshold to use for converting probabilities to binary
        predictions, by default 0.5.

    Returns
    -------
    float
        The Jaccard score.

    Notes
    -----
    This function is a wrapper around `sklearn.metrics.jaccard_score` that
    computes the Jaccard score for each sample and then averages over the
    samples.

    Note also that the y_score input is assumed to be an array of probabilities
    for each class. This function will convert the probabilities to binary
    predictions using the given threshold.
    """
    if y_true.ndim == 1:
        y_true = y_true[np.newaxis, :]

    if y_score.ndim == 1:
        y_score = y_score[np.newaxis, :]

    labels = np.arange(y_true.shape[1])

    return metrics.jaccard_score(
        y_true=y_true,
        y_pred=y_score > threshold,
        labels=labels,
        average="samples",
    )


def average_precision(
    y_true: np.ndarray,
    y_score: np.ndarray,
) -> float:
    """Compute the average precision score for the given true and predicted labels.

    Parameters
    ----------
    y_true
        True labels.
    y_score
        An array of predicted probabilities for each class.

    Returns
    -------
    float
        The average precision score.

    Notes
    -----
    This function is a wrapper around `sklearn.metrics.average_precision_score`
    that computes the average precision score for each sample and then averages
    over the samples.

    Note also that the y_score input is assumed to be an array of probabilities
    for each class.
    """
    return metrics.average_precision_score(  # type: ignore
        y_true=y_true,
        y_score=y_score,
        average="micro",
    )


def mean_average_precision(
    y_true: np.ndarray,
    y_score: np.ndarray,
) -> float:
    """Compute the mean average precision score for the given true and predicted labels.

    Parameters
    ----------
    y_true
        True labels.
    y_score
        An array of predicted probabilities for each class.

    Returns
    -------
    float
        The mean average precision score.

    Notes
    -----
    This function is a wrapper around `sklearn.metrics.average_precision_score`
    that computes the average precision score for each sample and then averages
    over the samples.

    Note also that the y_score input is assumed to be an array of probabilities
    for each class.
    """
    y_true = np.array(y_true).astype(np.float32)

    # Remove examples with no class
    no_class = np.isnan(y_true)
    y_true = y_true[~no_class]
    y_score = y_score[~no_class]

    if y_true.ndim == 1 and y_score.ndim == 2:
        # NOTE: In case the y_true input is one-dimensional (i.e. there
        # is a single correct class per example), we need to convert the
        # the input into a one-hot encoded matrix.
        num_classes = y_score.shape[1]
        y_true = np.eye(num_classes)[y_true.astype(np.int32)]

    return metrics.average_precision_score(  # type: ignore
        y_true=y_true,
        y_score=y_score,
        average="macro",
    )
