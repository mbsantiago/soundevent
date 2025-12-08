"""Algorithms for matching predictions to ground truths."""

from collections.abc import Callable
from dataclasses import astuple, dataclass
from itertools import product
from typing import (
    Generic,
    Iterable,
    Iterator,
    Sequence,
    Tuple,
    TypeVar,
)

import numpy as np
from scipy.optimize import linear_sum_assignment

from soundevent import data
from soundevent.evaluation.affinity import compute_affinity
from soundevent.geometry.match import select_greedy_matches

__all__ = [
    "match_geometries",
    "Match",
    "match_detections_and_gts",
]


GroundTruth = TypeVar("GroundTruth")
Detection = TypeVar("Detection")


@dataclass
class Match(Generic[Detection, GroundTruth]):
    """Result of matching a single prediction to a ground truth annotation.

    This tuple covers three possible scenarios:

    1. True Positive (TP): Both `prediction` and `annotation` are present.
       The `affinity_score` indicates the quality of the match.
    2. False Positive (FP): `prediction` is present, but `annotation` is None.
       This occurs when a prediction had no valid overlap with any ground truth
       (or its best matches were taken by higher-scoring predictions).
    3. False Negative (FN): `annotation` is present, but `prediction` is None.
       This occurs when a ground truth object was not matched by any
       prediction.

    Attributes
    ----------
    prediction
        The predicted object. If None, this represents a missed ground truth
        (FN).
    annotation
        The target object. If None, this represents a false alarm (FP).
    affinity_score
        The affinity (e.g., IoU) between the prediction and the annotation.
        Returns 0.0 if either the prediction or annotation is None.
    prediction_score
        The confidence score of the prediction. Returns 0.0 if the prediction
        is None.
    """

    prediction: Detection | None
    annotation: GroundTruth | None
    affinity_score: float
    prediction_score: float

    def __iter__(self):
        return iter(astuple(self))


def match_detections_and_gts(
    detections: Sequence[Detection],
    ground_truths: Sequence[GroundTruth],
    affinity: np.ndarray | Callable[[Detection, GroundTruth], float],
    affinity_threshold: float = 0,
    score: np.ndarray
    | Callable[[Detection], float]
    | Sequence[float]
    | None = None,
    strict_match: bool = False,
) -> Iterator[Match[Detection, GroundTruth]]:
    """Match predictions to ground truths greedily based on confidence scores.

    Parameters
    ----------
    detections
        A sequence of prediction objects.
    ground_truths
        A sequence of target objects to match against.
    affinity
        Either a precomputed (N_det, N_gt) affinity matrix or a function to
        compute the affinity score between a detection and a ground truth.
    affinity_threshold
        Matches with affinity <= threshold are discarded. Defaults to 0.0.
    score
        The confidence scores used to prioritise detections during greedy
        matching. Higher scores are processed first. This parameter accepts:

        * A sequence or array of scores corresponding to `detections`
            (must match the length and order of the input list).
        * A callable that extracts a float score from a single
            prediction object.
        * `None`: All predictions are assigned a score of 1.0, preserving
            the original input order.
    strict_match
        If True, prevents fallback to the second-best ground truth if the
        best one is taken.

    Yields
    ------
    EvaluationMatch
        A named tuple containing the matching results.

        * `prediction`: The ``Detection`` object (or None for false negatives).
        * `annotation`: The ``GroundTruth`` object (or None for false
        positives).
        * `affinity_score`: The score of the match (0.0 if unmatched).
        * `prediction_score`: The prediction confidence score (0.0 if
        unmatched).

        The iterator yields a "Full Outer Join" of the inputs: all predictions
        and all ground truths will appear exactly once in the output stream,
        either paired together or paired with None.
    """
    if score is not None:
        if callable(score):
            score = np.array([score(pred) for pred in detections])

        score = np.asarray(score)
        indices = np.argsort(score)[::-1]

        score = np.take(score, indices)
        detections = [detections[index] for index in indices]

        # If affinity is a pre-computed matrix, need to reorder its rows
        # according to the sorted indices.
        if isinstance(affinity, np.ndarray):
            affinity = np.take(affinity, indices, axis=0)

    else:
        score = np.ones(len(detections))

    affinity = _validate_affinity_matrix(
        detections,
        ground_truths,
        affinity,
    )

    for source_index, target_index, affinity_score in select_greedy_matches(
        affinity,
        strict=strict_match,
        threshold=affinity_threshold,
    ):
        pred = detections[source_index] if source_index is not None else None
        ann = ground_truths[target_index] if target_index is not None else None
        pred_score = score[source_index] if source_index is not None else 0
        yield Match(
            prediction=pred,
            annotation=ann,
            affinity_score=affinity_score,
            prediction_score=pred_score,
        )


def _validate_affinity_matrix(
    source: Sequence[Detection],
    target: Sequence[GroundTruth],
    affinity: np.ndarray | Callable[[Detection, GroundTruth], float],
) -> np.ndarray:
    n_rows = len(source)
    n_cols = len(target)

    if isinstance(affinity, np.ndarray):
        if affinity.shape != (n_rows, n_cols):
            raise ValueError(
                f"The affinity matrix has shape {affinity.shape}, but "
                f"should have shape ({n_rows}, {n_cols})."
            )

        return affinity

    affinity_matrix = np.zeros(shape=(n_rows, n_cols))

    for (index1, det), (index2, gt) in product(
        enumerate(source), enumerate(target)
    ):
        affinity_matrix[index1, index2] = affinity(det, gt)

    return affinity_matrix


def match_geometries(
    source: Sequence[data.Geometry],
    target: Sequence[data.Geometry],
    time_buffer: float = 0.01,
    freq_buffer: float = 100,
    affinity_threshold: float = 0,
) -> Iterable[Tuple[int | None, int | None, float]]:
    """Match geometries between a source and a target sequence.

    The matching is performed by first computing an affinity matrix between
    all pairs of source and target geometries. The affinity is a measure of
    similarity, calculated as the Intersection over Union (IoU). For more
    details on how affinity is computed, see
    [`soundevent.evaluation.affinity.compute_affinity`][soundevent.evaluation.affinity.compute_affinity].

    The affinity calculation is influenced by the `time_buffer` and
    `freq_buffer` parameters, which add a buffer to each geometry before
    comparison. This can help account for small variations in annotations.

    Once the affinity matrix is computed, the Hungarian algorithm (via
    `scipy.optimize.linear_sum_assignment`) is used to find an optimal
    assignment of source to target geometries that maximizes the total
    affinity.

    Finally, matches with an affinity below `affinity_threshold` are
    discarded and considered as unmatched.

    Parameters
    ----------
    source : Sequence[Geometry]
        The source geometries to match.
    target : Sequence[Geometry]
        The target geometries to match.
    time_buffer : float, optional
        A buffer in seconds added to each geometry when computing affinity.
        See
        [`soundevent.evaluation.affinity.compute_affinity`][soundevent.evaluation.affinity.compute_affinity]
        for more details. Defaults to 0.01.
    freq_buffer : float, optional
        A buffer in Hertz added to each geometry when computing affinity.
        See
        [`soundevent.evaluation.affinity.compute_affinity`][soundevent.evaluation.affinity.compute_affinity]
        for more details. Defaults to 100.
    affinity_threshold : float, optional
        The minimum affinity (IoU) for a pair of geometries to be
        considered a match. Pairs with affinity below this value are
        considered unmatched, by default 0.

    Returns
    -------
    Iterable[Tuple[Optional[int], Optional[int], float]]
        An iterable of matching results. Each source and target geometry is
        accounted for exactly once in the output. Each tuple can be one of:

        - ``(source_index, target_index, affinity)``: A successful match
          between a source and a target geometry with an affinity score.
        - ``(source_index, None, 0)``: An unmatched source geometry.
        - ``(None, target_index, 0)``: An unmatched target geometry.
    """
    # Compute the affinity between all pairs of geometries.
    cost_matrix = np.zeros(shape=(len(source), len(target)))
    for (index1, geometry1), (index2, geometry2) in product(
        enumerate(source), enumerate(target)
    ):
        cost_matrix[index1, index2] = compute_affinity(
            geometry1,
            geometry2,
            time_buffer=time_buffer,
            freq_buffer=freq_buffer,
        )

    # Select the matches that maximize the total affinity.
    matches = _select_matches(cost_matrix)

    for match1, match2 in matches:
        # If none were matched then affinity is 0
        if match1 is None or match2 is None:
            yield match1, match2, 0
            continue

        affinity = float(cost_matrix[match1, match2])

        # If it does not meet the threshold they should not be paired
        if affinity <= affinity_threshold:
            yield match1, None, 0
            yield None, match2, 0
        else:
            yield match1, match2, affinity


def _select_matches(
    cost_matrix: np.ndarray,
) -> Iterable[Tuple[int | None, int | None]]:
    """Select matches from a cost matrix.

    This function uses the Hungarian algorithm to find the optimal assignment of
    rows to columns that maximizes the sum of the costs. It then yields the
    matched pairs, as well as any unmatched rows and columns.

    Parameters
    ----------
    cost_matrix : np.ndarray
        The cost matrix.

    Returns
    -------
    Iterable[Tuple[Optional[int], Optional[int]]]
        An iterable of matches. Each match is a tuple of the row index and
        column index. If a row is not matched to any column, the column index
        is None. If a column is not matched to any row, the row index is
        None.
    """
    rows = set(range(cost_matrix.shape[0]))
    cols = set(range(cost_matrix.shape[1]))

    assiged_rows, assigned_columns = linear_sum_assignment(
        cost_matrix,
        maximize=True,
    )

    for row, column in zip(assiged_rows, assigned_columns, strict=True):
        yield row, column
        rows.remove(row)
        cols.remove(column)

    for row in rows:
        yield row, None

    for column in cols:
        yield None, column
