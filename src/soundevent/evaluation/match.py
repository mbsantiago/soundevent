"""Algorithms for matching geometries."""

from itertools import product
from typing import Iterable, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import linear_sum_assignment

from soundevent.data.geometries import Geometry
from soundevent.evaluation.affinity import compute_affinity

__all__ = [
    "match_geometries",
]


def match_geometries(
    source: Sequence[Geometry],
    target: Sequence[Geometry],
    time_buffer: float = 0.01,
    freq_buffer: float = 100,
    affinity_threshold: float = 0,
) -> Iterable[Tuple[Optional[int], Optional[int], float]]:
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
) -> Iterable[Tuple[Optional[int], Optional[int]]]:
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

    for row, column in zip(assiged_rows, assigned_columns):
        yield row, column
        rows.remove(row)
        cols.remove(column)

    for row in rows:
        yield row, None

    for column in cols:
        yield None, column
