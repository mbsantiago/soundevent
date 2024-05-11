"""Test suite for soundevent.evaluation.metrics.py."""

import numpy as np

from soundevent.evaluation import metrics


def test_jaccard_metric_for_single_example():
    """Test jaccard metric."""
    y_true = np.array([0, 1, 1, 0, 0])
    y_score = np.array([0.1, 0.9, 0.8, 0.1, 0.1])
    metric = metrics.jaccard(y_true=y_true, y_score=y_score)
    assert metric == 1


def test_jaccard_metric_for_multiple_examples():
    """Test jaccard metric."""
    y_true = np.array(
        [
            [0, 1, 1, 0, 0],
            [0, 0, 1, 1, 1],
        ]
    )
    y_score = np.array(
        [
            [0.1, 0.9, 0.8, 0.1, 0.1],
            [0.8, 0.2, 0.3, 0.7, 0.4],
        ]
    )
    metric = metrics.jaccard(y_true=y_true, y_score=y_score)
    assert metric == 0.625


def test_average_precision_1d():
    """Test average precision metric."""
    y_true = np.array([0, 1, 1, 0, 0])
    y_score = np.array([0.1, 0.9, 0.8, 0.1, 0.1])
    metric = metrics.average_precision(y_true=y_true, y_score=y_score)
    assert metric == 1


def test_average_precision_2d():
    """Test average precision metric."""
    y_true = np.array(
        [
            [0, 1, 1, 0, 0],
            [0, 0, 1, 1, 1],
        ]
    )
    y_score = np.array(
        [
            [0.1, 0.9, 0.8, 0.1, 0.1],
            [0.8, 0.2, 0.3, 0.7, 0.4],
        ]
    )
    metric = metrics.average_precision(y_true=y_true, y_score=y_score)
    assert metric == 0.81
