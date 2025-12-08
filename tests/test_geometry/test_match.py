import numpy as np
import pytest

from soundevent.data.geometries import TimeInterval
from soundevent.geometry.match import (
    match_geometries_greedy,
    match_geometries_optimal,
    select_greedy_matches,
    select_optimal_matches,
)


class TestMatchGeometriesOptimal:
    def test_perfect_match(self):
        source = [
            TimeInterval(coordinates=[0, 1]),
            TimeInterval(coordinates=[2, 3]),
        ]
        target = [
            TimeInterval(coordinates=[0, 1]),
            TimeInterval(coordinates=[2, 3]),
        ]

        matches = list(match_geometries_optimal(source, target))

        assert len(matches) == 2
        assert (0, 0, 1.0) in matches
        assert (1, 1, 1.0) in matches

    def test_no_overlap(self):
        source = [TimeInterval(coordinates=[0, 1])]
        target = [TimeInterval(coordinates=[2, 3])]

        matches = list(match_geometries_optimal(source, target))

        assert len(matches) == 2
        assert (0, None, 0.0) in matches
        assert (None, 0, 0.0) in matches

    def test_thresholding(self):
        source = [TimeInterval(coordinates=[0, 2])]
        target = [TimeInterval(coordinates=[1, 3])]

        matches = list(
            match_geometries_optimal(source, target, affinity_threshold=0.5)
        )

        assert len(matches) == 2
        assert (0, None, 0.0) in matches
        assert (None, 0, 0.0) in matches

        matches_low_threshold = list(
            match_geometries_optimal(source, target, affinity_threshold=0.1)
        )
        assert len(matches_low_threshold) == 1
        assert matches_low_threshold[0][0] == 0
        assert matches_low_threshold[0][1] == 0
        assert matches_low_threshold[0][2] == pytest.approx(1 / 3)

    def test_uneven_lists_more_source(self):
        source = [
            TimeInterval(coordinates=[0, 1]),
            TimeInterval(coordinates=[2, 3]),
        ]
        target = [TimeInterval(coordinates=[0, 1])]

        matches = list(match_geometries_optimal(source, target))

        assert len(matches) == 2
        expected_match = (0, 0, 1.0)
        expected_unmatched = (1, None, 0.0)

        assert expected_match in matches
        assert expected_unmatched in matches

    def test_uneven_lists_more_target(self):
        source = [TimeInterval(coordinates=[0, 1])]
        target = [
            TimeInterval(coordinates=[0, 1]),
            TimeInterval(coordinates=[2, 3]),
        ]

        matches = list(match_geometries_optimal(source, target))

        assert len(matches) == 2
        expected_match = (0, 0, 1.0)
        expected_unmatched = (None, 1, 0.0)

        assert expected_match in matches
        assert expected_unmatched in matches

    def test_custom_affinity_matrix(self):
        source = [TimeInterval(coordinates=[0, 1])]
        target = [TimeInterval(coordinates=[0, 1])]

        # Matrix says they don't match (score 0), ignoring actual geometry
        affinity = np.array([[0.0]])

        matches = list(
            match_geometries_optimal(source, target, affinity=affinity)
        )

        # Since score 0 <= threshold 0, they should be unmatched
        assert (0, None, 0.0) in matches
        assert (None, 0, 0.0) in matches


class TestMatchGeometriesGreedy:
    def test_greedy_behavior_differs_from_optimal(self):
        source = [TimeInterval(coordinates=[0, 1])] * 2
        target = [TimeInterval(coordinates=[0, 1])] * 2

        affinity_matrix = np.array([[0.8, 0.5], [0.9, 0.1]])

        greedy_matches = list(
            match_geometries_greedy(source, target, affinity=affinity_matrix)
        )
        assert greedy_matches == [(0, 0, 0.8), (1, 1, 0.1)]

        optimal_matches = list(
            match_geometries_optimal(source, target, affinity=affinity_matrix)
        )
        assert optimal_matches == [(0, 1, 0.5), (1, 0, 0.9)]

    def test_order_dependence(self):
        source = [TimeInterval(coordinates=[0, 1])] * 2
        target = [TimeInterval(coordinates=[0, 1])] * 2

        affinity_matrix = np.array(
            [
                [0.8, 0.5],
                [0.9, 0.1],
            ]
        )
        matches_1 = list(
            match_geometries_greedy(
                source,
                target,
                affinity=affinity_matrix,
            )
        )

        affinity_matrix_reversed = np.array(
            [
                [0.9, 0.1],
                [0.8, 0.5],
            ]
        )

        matches_2 = list(
            match_geometries_greedy(
                source,
                target,
                affinity=affinity_matrix_reversed,
            )
        )
        assert matches_1 != matches_2


class TestSelectOptimalMatches:
    def test_square_matrix(self):
        matrix = np.array([[1.0, 0.0], [0.0, 1.0]])
        matches = list(select_optimal_matches(matrix))
        assert (0, 0, 1.0) in matches
        assert (1, 1, 1.0) in matches

    def test_rectangular_more_rows(self):
        matrix = np.array([[1.0], [0.5]])
        matches = list(select_optimal_matches(matrix))
        assert (0, 0, 1.0) in matches
        assert (1, None, 0.0) in matches

    def test_rectangular_more_cols(self):
        matrix = np.array([[1.0, 0.5]])
        matches = list(select_optimal_matches(matrix))
        assert (0, 0, 1.0) in matches
        assert (None, 1, 0.0) in matches

    def test_zero_matrix(self):
        matrix = np.zeros((2, 2))
        matches = list(select_optimal_matches(matrix))
        matched_rows = [m[0] for m in matches if m[0] is not None]
        matched_cols = [m[1] for m in matches if m[1] is not None]
        assert len(matched_rows) == 2
        assert len(matched_cols) == 2
        assert all(score == 0.0 for _, _, score in matches)

    def test_matrix_with_no_rows(self):
        matrix = np.zeros((0, 2))
        matches = list(select_optimal_matches(matrix))
        assert len(matches) == 2
        assert (None, 0, 0.0) in matches
        assert (None, 1, 0.0) in matches

    def test_matrix_with_no_cols(self):
        matrix = np.zeros((2, 0))
        matches = list(select_optimal_matches(matrix))
        assert len(matches) == 2
        assert (0, None, 0.0) in matches
        assert (1, None, 0.0) in matches

    def test_threshold(self):
        matrix = np.array([[1.0, 0.4], [0.4, 0.3]])
        matches = list(select_optimal_matches(matrix, threshold=0.5))
        assert (0, 0, 1.0) in matches
        assert (1, None, 0.0) in matches
        assert (None, 1, 0.0) in matches

    def test_threshold_exact(self):
        matrix = np.array([[0.5]])
        matches = list(select_optimal_matches(matrix, threshold=0.5))
        assert (0, None, 0.0) in matches
        assert (None, 0, 0.0) in matches

    def test_threshold_all_filtered(self):
        matrix = np.array([[0.1, 0.1], [0.1, 0.1]])
        matches = list(select_optimal_matches(matrix, threshold=0.5))
        assert len(matches) == 4
        assert all(
            source is None or target is None for source, target, _ in matches
        )
        assert all(score == 0.0 for _, _, score in matches)


class TestSelectGreedyMatches:
    def test_square_matrix(self):
        matrix = np.array([[0.9, 0.1], [0.8, 0.5]])
        matches = list(select_greedy_matches(matrix))
        assert (0, 0, 0.9) in matches
        assert (1, 1, 0.5) in matches

    def test_matrix_more_rows(self):
        matrix = np.array([[1.0], [0.5]])
        matches = list(select_greedy_matches(matrix))
        assert (0, 0, 1.0) in matches
        assert (1, None, 0.0) in matches

    def test_matrix_more_cols(self):
        matrix = np.array([[1.0, 0.5]])
        matches = list(select_greedy_matches(matrix))
        assert len(matches) == 2
        assert (0, 0, 1.0) in matches
        assert (None, 1, 0.0) in matches

    def test_empty_matrix(self):
        matrix = np.zeros((0, 0))
        matches = list(select_greedy_matches(matrix))
        assert len(matches) == 0

    def test_matrix_with_no_rows(self):
        matrix = np.zeros((0, 2))
        matches = list(select_greedy_matches(matrix))
        assert len(matches) == 2
        assert (None, 0, 0.0) in matches
        assert (None, 1, 0.0) in matches

    def test_matrix_with_no_cols(self):
        matrix = np.zeros((2, 0))
        matches = list(select_greedy_matches(matrix))
        assert len(matches) == 2
        assert (0, None, 0.0) in matches
        assert (1, None, 0.0) in matches

    def test_strict_conflict_behavior(self):
        matrix = np.array([[1.0, 0.0], [0.9, 0.5]])

        matches_default = list(select_greedy_matches(matrix, strict=False))
        assert (0, 0, 1.0) in matches_default
        assert (1, 1, 0.5) in matches_default
        assert len(matches_default) == 2

        matches_strict = list(select_greedy_matches(matrix, strict=True))
        assert (0, 0, 1.0) in matches_strict
        assert (1, None, 0.0) in matches_strict
        assert (None, 1, 0.0) in matches_strict

    def test_strict_no_conflict(self):
        matrix = np.array([[1.0, 0.0], [0.0, 1.0]])
        matches = list(select_greedy_matches(matrix, strict=True))
        assert (0, 0, 1.0) in matches
        assert (1, 1, 1.0) in matches
        assert len(matches) == 2

    def test_strict_multi_row_contention(self):
        matrix = np.array(
            [
                [1.0, 0.5, 0.1],
                [0.9, 0.5, 0.1],
                [0.8, 0.5, 0.1],
            ]
        )

        matches = list(select_greedy_matches(matrix, strict=True))
        assert (0, 0, 1.0) in matches
        assert (1, None, 0.0) in matches
        assert (2, None, 0.0) in matches
        assert (None, 1, 0.0) in matches
        assert (None, 2, 0.0) in matches

    def test_threshold(self):
        matrix = np.array([[1.0, 0.5], [0.4, 0.8]])
        matches = list(select_greedy_matches(matrix, threshold=0.9))
        assert (0, 0, 1.0) in matches
        assert (1, None, 0.0) in matches
        assert (None, 1, 0.0) in matches

    def test_threshold_strict(self):
        matrix = np.array(
            [
                [0.8, 0.9],
                [0.8, 0.4],
            ]
        )
        matches = list(
            select_greedy_matches(matrix, strict=True, threshold=0.85)
        )
        assert (0, 1, 0.9) in matches
        assert (1, None, 0.0) in matches
        assert (None, 0, 0.0) in matches

    def test_threshold_exact(self):
        matrix = np.array([[0.5]])
        matches = list(select_greedy_matches(matrix, threshold=0.5))
        assert (0, None, 0.0) in matches
        assert (None, 0, 0.0) in matches

    def test_threshold_all_filtered(self):
        matrix = np.array([[0.4, 0.4], [0.4, 0.4]])
        matches = list(select_greedy_matches(matrix, threshold=0.5))
        assert len(matches) == 4
        assert all(
            source is None or target is None for source, target, _ in matches
        )
        assert all(score == 0.0 for _, _, score in matches)


class TestAffinityValidation:
    def test_invalid_shape(self):
        source = [TimeInterval(coordinates=[0, 1])]
        target = [TimeInterval(coordinates=[0, 1])]
        affinity = np.zeros((2, 2))

        with pytest.raises(ValueError, match="shape"):
            list(match_geometries_optimal(source, target, affinity=affinity))
