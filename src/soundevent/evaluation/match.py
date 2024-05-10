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
) -> Iterable[Tuple[Optional[int], Optional[int], float]]:
    """Match geometries.

    This function matches geometries from a source and target sequence.
    The geometries are matched based on their affinity, which is computed
    using the compute_affinity function. The final matches are then
    selected to maximize the total affinity between the source and target
    geometries.

    Parameters
    ----------
    source : Sequence[Geometry]
        Source geometries.
    target : Sequence[Geometry]
        Target geometries.

    Returns
    -------
    Sequence[Tuple[Optional[int], Optional[int], float]]
        A sequence of matches. Each match is a tuple of the source index,
        target index and affinity. If a source geometry is not matched to
        any target geometry, the target index is None. If a target geometry
        is not matched to any source geometry, the source index is None.
        Every source and target geometry is matched exactly once.
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
        affinity = 0.0
        if match1 is not None and match2 is not None:
            # If the source or target match is None, the affinity is 0.
            affinity = float(cost_matrix[match1, match2])

        yield match1, match2, affinity


def _select_matches(
    cost_matrix: np.ndarray,
) -> Iterable[Tuple[Optional[int], Optional[int]]]:
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
