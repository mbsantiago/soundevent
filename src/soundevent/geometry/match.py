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
from typing import Iterable, Sequence, Set, Tuple

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
    affinity: np.ndarray | AffinityFn | None = None,
    affinity_threshold: float = 0,
) -> Iterable[Tuple[int | None, int | None, float]]:
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

    matches = select_optimal_matches(
        affinity_matrix,
        threshold=affinity_threshold,
    )

    for match1, match2, affinity_score in matches:
        yield match1, match2, affinity_score


def match_geometries_greedy(
    source: Sequence[Geometry],
    target: Sequence[Geometry],
    affinity: np.ndarray | AffinityFn | None = None,
    affinity_threshold: float = 0,
    strict: bool = False,
) -> Iterable[Tuple[int | None, int | None, float]]:
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
    strict : bool, optional
        Determines the matching behavior when the best target is already taken:
        - If ``False`` (default), the algorithm finds the next best
          available target (best available match).
        - If ``True``, the source is left unmatched (best match or nothing).

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

    matches = select_greedy_matches(
        affinity_matrix,
        strict=strict,
        threshold=affinity_threshold,
    )

    for match1, match2, affinity_score in matches:
        yield match1, match2, affinity_score


def _validate_affinity_matrix(
    source: Sequence[Geometry],
    target: Sequence[Geometry],
    affinity: np.ndarray | AffinityFn | None,
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
    threshold: float = 0,
) -> Iterable[Tuple[int | None, int | None, float]]:
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
    affinity_score : float
        The affinity score between the matched rows and columns. Returns 0
        for unmatched items.

    Notes
    -----
    This functions uses the Jonker-Volgenant algorithm via SciPy's
    [`linear_sum_assignment`][scipy.optimize.linear_sum_assignment].
    """
    rows = set(range(affinity_matrix.shape[0]))
    cols = set(range(affinity_matrix.shape[1]))

    assigned_rows, assigned_columns = linear_sum_assignment(
        affinity_matrix,
        maximize=True,
    )

    for row, column in zip(assigned_rows, assigned_columns, strict=True):
        value = float(affinity_matrix[row, column])

        # Ignore matches with affinity below the threshold
        if value <= threshold:
            continue

        yield row, column, value
        rows.remove(row)
        cols.remove(column)

    for row in rows:
        yield row, None, 0

    for column in cols:
        yield None, column, 0


def select_greedy_matches(
    affinity_matrix: np.ndarray,
    strict: bool = False,
    threshold: float = 0,
) -> Iterable[Tuple[int | None, int | None, float]]:
    """Select matches greedily based on the row order.

    Parameters
    ----------
    affinity_matrix : np.ndarray
        A 2D array of scores where rows represent sources and columns
        represent targets.
    strict : bool, optional
        Determines the matching behavior when the best column is already taken:
        - If ``False`` (default), the algorithm finds the next best
          available column (best available match).
        - If ``True``, the row is left unmatched (best match or nothing).
    threshold : float, optional
        The lower bound for a valid match. Matches with affinity less than or
        equal to this value are discarded. Defaults to 0 (discarding
        zero-affinity matches).

    Yields
    ------
    row_index : int or None
        The row index. If ``None``, this indicates a leftover column that
        was not matched.
    col_index : int or None
        The column index. If ``None``, this indicates a row that could
        not be matched.
    affinity_score : float
        The affinity score between the matched rows and columns. Returns 0
        for unmatched items.

    Notes
    -----
    This algorithm iterates over rows 0 to N. Because matches are consumed
    greedily, the order of the rows in the input matrix affects the outcome.
    """
    n_rows, n_cols = affinity_matrix.shape
    available_cols = set(range(n_cols))

    if n_rows == 0:
        for col in available_cols:
            yield None, col, 0
        return

    if n_cols == 0:
        for row in range(n_rows):
            yield row, None, 0
        return

    for index, row in enumerate(affinity_matrix):
        # If there are no columns left, return None
        if not available_cols:
            yield index, None, 0
            continue

        # Select the best column
        col, score = _select_greedy_match(
            row,
            available_cols,
            strict=strict,
            threshold=threshold,
        )

        if col is None:
            # If no column is available return None
            yield index, None, 0
            continue

        # Yield the selected column and mark it as assigned
        yield index, col, score
        available_cols.remove(col)

    for missing_col in available_cols:
        yield None, missing_col, 0


def _select_greedy_match(
    row: np.ndarray,
    available_cols: Set[int],
    strict: bool = False,
    threshold: float = 0,
) -> Tuple[int | None, float]:
    """Find the best available column for a single row."""
    if strict:
        best_col = int(np.argmax(row))
        score = float(row[best_col])

        if best_col not in available_cols or score <= threshold:
            return None, 0

        return best_col, score

    sorted_indices = np.argsort(row)[::-1]

    for col_index in sorted_indices:
        score = float(row[col_index])

        # Stop if the score is too low
        if score <= threshold:
            break

        if col_index not in available_cols:
            continue

        return int(col_index), score

    return None, 0
