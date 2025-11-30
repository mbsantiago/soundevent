"""Algorithms for matching geometries.

This module provides tools to match two sets of geometries (e.g., predicted
sound events vs. ground truth annotations) based on their similarity or
"affinity".

The matching process generally involves three steps:

1.  **Affinity Computation**: Calculating a score (like IoU) between every
    pair of source and target geometries.
2.  **Selection**: Choosing which pairs constitute a "match" based on a
    strategy (Optimal vs. Greedy).
3.  **Thresholding**: Discarding matches that have a score below a certain
    value.

Main Functions
--------------
* [`match_geometries_optimal`][soundevent.geometry.match_geometries_optimal]:
    Finds the global best set of matches using the Hungarian algorithm.
* [`match_geometries_greedy`][soundevent.geometry.match_geometries_greedy]:
    Matches geometries sequentially in the order they appear. This is faster but
    order-dependent.

Both functions yield tuples of ``(source_index, target_index, score)``.
"""

from itertools import product
from typing import Iterable, Optional, Sequence, Tuple, Union

import numpy as np
from scipy.optimize import linear_sum_assignment

from soundevent.data.geometries import Geometry
from soundevent.geometry.affinity import AffinityFn, compute_geometric_iou

__all__ = [
    "match_geometries_optimal",
    "match_geometries_greedy",
    "select_optimal_matches",
    "select_greedy_matches",
]


def match_geometries_optimal(
    source: Sequence[Geometry],
    target: Sequence[Geometry],
    affinity: Union[np.ndarray, AffinityFn, None] = None,
    affinity_threshold: float = 0,
) -> Iterable[Tuple[Optional[int], Optional[int], float]]:
    """Match geometries to maximize total affinity.

    Parameters
    ----------
    source
        The list of source geometries.
    target
        The list of target geometries.
    affinity
        How to compute the affinity score between geometries. Can be a function
        taking two geometries and returning a float, or a pre-computed affinity
        matrix. If None, defaults to [geometric
        IoU][soundevent.geometry.compute_geometric_iou].
    affinity_threshold
        The minimum score required to consider a match valid. Pairs with a
        score below this will be returned as unmatched. Defaults to 0.

    Yields
    ------
    source_index : int or None
        The index of the geometry in the ``source`` list. Is ``None`` if a
        target geometry remains unmatched.
    target_index : int or None
        The index of the geometry in the ``target`` list. Is ``None`` if a
        source geometry remains unmatched.
    score : float
        The affinity score between the matched geometries. Returns 0.0 for
        unmatched items.

    Notes
    -----
    This function solves the linear assignment problem. It finds the unique
    set of pairings that maximizes the sum of affinity scores for the
    entire group. This is computationally more expensive than greedy matching
    but ensures the best global result.
    """
    affinity_matrix = _validate_affinity_matrix(source, target, affinity)

    matches = select_optimal_matches(affinity_matrix)

    for match1, match2 in matches:
        # If not matched then affinity is 0
        if match1 is None or match2 is None:
            yield match1, match2, 0
            continue

        affinity_score = float(affinity_matrix[match1, match2])

        # If it does not meet the threshold they should not be paired
        if affinity_score <= affinity_threshold:
            yield match1, None, 0
            yield None, match2, 0
            continue

        yield match1, match2, affinity_score


def match_geometries_greedy(
    source: Sequence[Geometry],
    target: Sequence[Geometry],
    affinity: Union[np.ndarray, AffinityFn, None] = None,
    affinity_threshold: float = 0,
) -> Iterable[Tuple[Optional[int], Optional[int], float]]:
    """Match geometries using a greedy strategy.

    Parameters
    ----------
    source
        The list of source geometries.
    target
        The list of target geometries.
    affinity
        How to compute the affinity score between geometries. Can be a function
        or a pre-computed matrix. If None, defaults to [geometric
        IoU][soundevent.geometry.compute_geometric_iou].
    affinity_threshold
        The minimum score required to consider a match valid.

    Yields
    ------
    source_index : int or None
        The index of the geometry in the ``source`` list. Is ``None`` if a
        target geometry remains unmatched.
    target_index : int or None
        The index of the geometry in the ``target`` list. Is ``None`` if a
        source geometry remains unmatched.
    score : float
        The affinity score between the matched geometries. Returns 0.0 for
        unmatched items.

    Notes
    -----
    This function iterates through the `source` list in order. For each
    geometry, it picks the available `target` with the highest affinity.
    Once a target is matched, it cannot be used again.

    Because this is done sequentially, the order of the input list matters.
    A geometry early in the list might match a target that would have been
    a better match for a geometry later in the list.
    """
    affinity_matrix = _validate_affinity_matrix(source, target, affinity)

    matches = select_greedy_matches(affinity_matrix)

    for match1, match2 in matches:
        # If not matched then affinity is 0
        if match1 is None or match2 is None:
            yield match1, match2, 0
            continue

        affinity_score = float(affinity_matrix[match1, match2])

        # If it does not meet the threshold they should not be paired
        if affinity_score <= affinity_threshold:
            yield match1, None, 0
            yield None, match2, 0
            continue

        yield match1, match2, affinity_score


def _validate_affinity_matrix(
    source: Sequence[Geometry],
    target: Sequence[Geometry],
    affinity: Union[np.ndarray, AffinityFn, None],
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

    affinity_fn = affinity or compute_geometric_iou
    affinity_matrix = np.zeros(shape=(n_rows, n_cols))

    for (index1, geometry1), (index2, geometry2) in product(
        enumerate(source), enumerate(target)
    ):
        affinity_matrix[index1, index2] = affinity_fn(geometry1, geometry2)

    return affinity_matrix


def select_optimal_matches(
    affinity_matrix: np.ndarray,
) -> Iterable[Tuple[Optional[int], Optional[int]]]:
    """Find the optimal assignment that maximizes the total affinity score.

    Parameters
    ----------
    affinity_matrix : np.ndarray
        A 2D array where `M[i, j]` represents the score/affinity between
        row `i` and column `j`.

    Yields
    ------
    row_index : int or None
        The row index (source).
    col_index : int or None
        The column index (target).

    Notes
    -----
    This functions uses the Jonker-Volgenant algorithm via SciPy's
    [`linear_sum_assignment`][scipy.optimize.linear_sum_assignment].
    """
    rows = set(range(affinity_matrix.shape[0]))
    cols = set(range(affinity_matrix.shape[1]))

    assiged_rows, assigned_columns = linear_sum_assignment(
        affinity_matrix,
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


def select_greedy_matches(
    affinity_matrix: np.ndarray,
) -> Iterable[Tuple[Optional[int], Optional[int]]]:
    """Select matches greedily based on the row order.

    Parameters
    ----------
    affinity_matrix : np.ndarray
        A 2D array of scores.

    Yields
    ------
    row_index : int or None
        The row index (source).
    col_index : int or None
        The column index (target).

    Notes
    -----
    This iterates over rows 0 to N. For each row, it selects the column
    with the highest value that hasn't already been assigned.
    """
    rows = set(range(affinity_matrix.shape[0]))
    cols = set(range(affinity_matrix.shape[1]))

    for index, row in enumerate(affinity_matrix):
        # Mark row as assigned
        rows.remove(index)

        # Sort indices by affinity descending
        sorted_indices = np.argsort(row)[::-1]

        for col_index in sorted_indices:
            # If the column is already assigned, skip it
            if col_index not in cols:
                continue

            yield index, int(col_index)
            cols.remove(col_index)
            break
        else:
            yield index, None

        # Stop when all columns are assigned
        if len(cols) == 0:
            break

    for misisng_row in rows:
        yield misisng_row, None
