"""Test suite for geometry matching functions."""

import math

from soundevent import data
from soundevent.evaluation import match_geometries


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
    matches = list(match_geometries([target], [option1, option2]))

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
