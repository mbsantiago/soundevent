"""Test suite for geometry matching functions."""

import math
from typing import NamedTuple

import numpy as np

from soundevent import data
from soundevent.evaluation import match_geometries
from soundevent.evaluation.match import Match, match_detections_and_gts


class Box(NamedTuple):
    """A simple mock object for testing."""

    score: float
    id: int


def simple_affinity(pred: Box, gt: Box) -> float:
    """Return 1.0 if IDs match, else 0.0."""
    return 1.0 if pred.id == gt.id else 0.0


def test_time_stamp_is_supported():
    timestamp = data.TimeStamp(coordinates=1)
    matches = list(match_geometries([timestamp], [timestamp]))
    assert len(matches) == 1
    source_index, target_index, affinity = matches[0]
    assert source_index == 0
    assert target_index == 0
    assert affinity == 1.0


def test_time_interval_is_supported():
    time_interval = data.TimeInterval(coordinates=[1, 2])
    matches = list(match_geometries([time_interval], [time_interval]))
    assert len(matches) == 1
    source_index, target_index, affinity = matches[0]
    assert source_index == 0
    assert target_index == 0
    assert affinity == 1.0


def test_point_is_supported():
    point = data.Point(coordinates=[1, 2])
    matches = list(match_geometries([point], [point]))
    assert len(matches) == 1
    source_index, target_index, affinity = matches[0]
    assert source_index == 0
    assert target_index == 0
    assert math.isclose(affinity, 1.0)


def test_line_string_is_supported():
    line_string = data.LineString(coordinates=[[1, 2], [3, 4]])
    matches = list(match_geometries([line_string], [line_string]))
    assert len(matches) == 1
    source_index, target_index, affinity = matches[0]
    assert source_index == 0
    assert target_index == 0
    assert affinity == 1.0


def test_bounding_box_is_supported():
    bounding_box = data.BoundingBox(coordinates=[1, 3, 2, 4])
    matches = list(match_geometries([bounding_box], [bounding_box]))
    assert len(matches) == 1
    source_index, target_index, affinity = matches[0]
    assert source_index == 0
    assert target_index == 0
    assert affinity == 1.0


def test_polygon_is_supported():
    polygon = data.Polygon(coordinates=[[[1, 2], [4, 3], [5, 6], [1, 2]]])
    matches = list(match_geometries([polygon], [polygon]))
    assert len(matches) == 1
    source_index, target_index, affinity = matches[0]
    assert source_index == 0
    assert target_index == 0
    assert affinity == 1.0


def test_multi_point_is_supported():
    multi_point = data.MultiPoint(coordinates=[[1, 2], [3, 4]])
    matches = list(
        match_geometries(
            [multi_point],
            [multi_point],
            time_buffer=0.01,
            freq_buffer=0.01,
        )
    )
    assert len(matches) == 1
    source_index, target_index, affinity = matches[0]
    assert source_index == 0
    assert target_index == 0
    assert math.isclose(affinity, 1.0)


def test_multi_linestring_is_supported():
    multi_linestring = data.MultiLineString(
        coordinates=[[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
    )
    matches = list(match_geometries([multi_linestring], [multi_linestring]))
    assert len(matches) == 1
    source_index, target_index, affinity = matches[0]
    assert source_index == 0
    assert target_index == 0
    assert affinity == 1.0


def test_multi_polygon_is_supported():
    multi_polygon = data.MultiPolygon(
        coordinates=[[[[1, 2], [4, 3], [5, 6], [1, 2]]]]
    )
    matches = list(match_geometries([multi_polygon], [multi_polygon]))
    assert len(matches) == 1
    source_index, target_index, affinity = matches[0]
    assert source_index == 0
    assert target_index == 0
    assert affinity == 1.0


def test_best_affinity_is_selected_multiple_sources():
    target = data.BoundingBox(coordinates=[4, 4, 8, 8])
    option1 = data.BoundingBox(coordinates=[3, 3, 5, 5])
    option2 = data.BoundingBox(coordinates=[5, 5, 9, 9])
    matches = list(match_geometries([option1, option2], [target]))

    assert len(matches) == 2

    source_index, target_index, affinity = matches[0]
    assert source_index == 1
    assert target_index == 0
    assert affinity > 0

    # Option 1 should not be matched
    source_index, target_index, affinity = matches[1]
    assert source_index == 0
    assert target_index is None
    assert affinity == 0


def test_best_affinity_is_selected_multiple_targets():
    target = data.BoundingBox(coordinates=[4, 4, 8, 8])
    option1 = data.BoundingBox(coordinates=[3, 3, 5, 5])
    option2 = data.BoundingBox(coordinates=[5, 5, 9, 9])
    matches = list(
        match_geometries(
            [target],
            [option1, option2],
            affinity_threshold=0,
        )
    )

    assert len(matches) == 2

    source_index, target_index, affinity = matches[0]
    assert source_index == 0
    assert target_index == 1
    assert affinity > 0

    # Option 1 should not be matched
    source_index, target_index, affinity = matches[1]
    assert source_index is None
    assert target_index == 0
    assert affinity == 0


def test_geometries_with_zero_affinity_are_not_matched():
    target = data.BoundingBox(coordinates=[4, 4, 8, 8])
    option = data.BoundingBox(coordinates=[10, 4, 14, 8])

    matches = list(match_geometries([target], [option]))

    assert len(matches) == 2
    assert all(affinity == 0 for _, _, affinity in matches)


def test_affinity_threshold_can_be_modified():
    # Two 4x4 geometries with 2x4 overlap and 6x4 union.
    # IOU should be 1/3
    target = data.BoundingBox(coordinates=[4, 4, 8, 8])
    option = data.BoundingBox(coordinates=[6, 4, 10, 8])

    # Should match with low IOU
    matches = list(
        match_geometries(
            [target],
            [option],
            time_buffer=0,
            freq_buffer=0,
            affinity_threshold=0.25,
        )
    )
    assert len(matches) == 1
    source_index, target_index, affinity = matches[0]
    assert source_index is not None
    assert target_index is not None
    assert affinity == 1 / 3

    # Should not match with high IOU
    matches = list(
        match_geometries(
            [target],
            [option],
            time_buffer=0,
            freq_buffer=0,
            affinity_threshold=0.5,
        )
    )
    assert len(matches) == 2
    assert all(affinity == 0 for _, _, affinity in matches)


class TestMatchDetectionsAndGts:
    def test_score_based_priority(self):
        """Verify high-score predictions get priority for the same GT."""
        gt = Box(score=0, id=1)

        pred_low_conf = Box(score=0.5, id=1)
        pred_high_conf = Box(score=0.9, id=1)

        matches = list(
            match_detections_and_gts(
                detections=[pred_low_conf, pred_high_conf],
                ground_truths=[gt],
                affinity=simple_affinity,
                score=lambda x: x.score,
            )
        )

        assert len(matches) == 2

        tp_match = next(m for m in matches if m.prediction == pred_high_conf)
        assert tp_match.annotation == gt
        assert tp_match.prediction_score == 0.9

        fp_match = next(m for m in matches if m.prediction == pred_low_conf)
        assert fp_match.annotation is None
        assert fp_match.prediction_score == 0.5

    def test_full_outer_join_accounting(self):
        """Verify every input appears exactly once in the output."""
        p1 = Box(score=0.8, id=1)
        p2 = Box(score=0.7, id=99)

        g1 = Box(score=0, id=1)
        g2 = Box(score=0, id=55)

        matches = list(
            match_detections_and_gts(
                detections=[p1, p2],
                ground_truths=[g1, g2],
                affinity=simple_affinity,
                score=lambda x: x.score,
            )
        )

        assert len(matches) == 3

        match_tp = next(m for m in matches if m.prediction == p1)
        assert match_tp.annotation == g1

        match_fp = next(m for m in matches if m.prediction == p2)
        assert match_fp.annotation is None

        match_fn = next(m for m in matches if m.annotation == g2)
        assert match_fn.prediction is None
        assert match_fn.prediction_score == 0.0

    def test_output_data_structure_values(self):
        """Verify Match object fields are correct."""
        p1 = Box(score=0.85, id=1)
        g1 = Box(score=0, id=1)

        match = next(
            match_detections_and_gts(
                detections=[p1],
                ground_truths=[g1],
                affinity=simple_affinity,
                score=lambda x: x.score,
            )
        )

        assert isinstance(match, Match)
        assert match.prediction == p1
        assert match.annotation == g1
        assert match.affinity_score == 1.0
        assert match.prediction_score == 0.85

    def test_score_as_numpy_array(self):
        """Verify correct behavior when score is provided as a numpy array."""
        gt = Box(score=0, id=1)
        pred1 = Box(score=1, id=1)
        pred2 = Box(score=2, id=1)

        detections = [pred1, pred2]
        scores = np.array([0.1, 0.9])

        matches = list(
            match_detections_and_gts(
                detections=detections,
                ground_truths=[gt],
                affinity=simple_affinity,
                score=scores,
            )
        )

        assert len(matches) == 2

        tp_match = next(m for m in matches if m.prediction == pred2)
        assert tp_match.annotation == gt
        assert tp_match.prediction_score == 0.9

        fp_match = next(m for m in matches if m.prediction == pred1)
        assert fp_match.annotation is None
        assert fp_match.prediction_score == 0.1

    def test_score_none_uses_ones_array(self):
        """Verify behavior when score is None (defaults to all ones)."""
        gt1 = Box(score=0, id=1)
        gt2 = Box(score=0, id=2)

        pred1 = Box(score=0.1, id=1)
        pred2 = Box(score=0.9, id=2)

        detections = [pred1, pred2]
        ground_truths = [gt1, gt2]

        matches = list(
            match_detections_and_gts(
                detections=detections,
                ground_truths=ground_truths,
                affinity=simple_affinity,
                score=None,
            )
        )

        assert len(matches) == 2

        tp_match1 = next(m for m in matches if m.prediction == pred1)
        assert tp_match1.annotation == gt1
        assert tp_match1.prediction_score == 1.0

        tp_match2 = next(m for m in matches if m.prediction == pred2)
        assert tp_match2.annotation == gt2
        assert tp_match2.prediction_score == 1.0

    def test_affinity_as_function(self):
        """Verify behavior when affinity is a callable."""
        pred1 = {"name": "pred1", "score": 1.0, "time": 0}
        pred2 = {"name": "pred2", "score": 0.9, "time": 1}
        gt1 = {"name": "gt1", "time": 1}
        gt2 = {"name": "gt2", "time": 0}

        matches = list(
            match_detections_and_gts(
                detections=[pred1, pred2],
                ground_truths=[gt1, gt2],
                affinity=lambda pred, gt: 1 - abs(pred["time"] - gt["time"]),
                score=lambda pred: pred["score"],
            )
        )

        assert len(matches) == 2
        assert matches[0].prediction == pred1
        assert matches[0].annotation == gt2
        assert matches[0].affinity_score == 1.0

        assert matches[1].prediction == pred2
        assert matches[1].annotation == gt1
        assert matches[1].affinity_score == 1.0

    def test_affinity_as_precomputed_matrix(self):
        """Verify behavior when affinity is a precomputed matrix."""
        pred1 = {"name": "pred1", "score": 1.0, "time": 0}
        pred2 = {"name": "pred2", "score": 0.9, "time": 1}
        gt1 = {"name": "gt1", "time": 1}
        gt2 = {"name": "gt2", "time": 0}

        matrix = np.array(
            [
                [1.0, 0.0],
                [0.0, 1.0],
            ]
        )

        matches = list(
            match_detections_and_gts(
                detections=[pred1, pred2],
                ground_truths=[gt1, gt2],
                affinity=matrix,
                score=lambda pred: pred["score"],
            )
        )

        assert len(matches) == 2
        assert matches[0].prediction == pred1
        assert matches[0].annotation == gt1
        assert matches[0].affinity_score == 1.0

        assert matches[1].prediction == pred2
        assert matches[1].annotation == gt2
        assert matches[1].affinity_score == 1.0
