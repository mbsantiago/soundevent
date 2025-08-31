"""Test suite for geometry functions."""

import json
from dataclasses import dataclass
from typing import List

import pytest

from soundevent import data


def test_load_timestamp_from_json():
    """Test that a TimeStamp can be loaded from JSON."""
    obj = json.dumps({"type": "TimeStamp", "coordinates": 0})
    geom = data.geometry_validate(obj, mode="json")
    assert isinstance(geom, data.TimeStamp)
    assert geom.coordinates == 0


def test_load_timestamp_from_dict():
    """Test that a TimeStamp can be loaded from a dictionary."""
    obj = {"type": "TimeStamp", "coordinates": 0}
    geom = data.geometry_validate(obj, mode="dict")
    assert isinstance(geom, data.TimeStamp)
    assert geom.coordinates == 0


def test_load_timestamp_from_attributes():
    """Test that a TimeStamp can be loaded from attributes."""
    obj = data.TimeStamp(coordinates=0)
    geom = data.geometry_validate(obj, mode="attributes")
    assert isinstance(geom, data.TimeStamp)
    assert geom.coordinates == 0


def test_load_timeinterval_from_json():
    """Test that a TimeInterval can be loaded from JSON."""
    obj = json.dumps({"type": "TimeInterval", "coordinates": [0, 1]})
    geom = data.geometry_validate(obj, mode="json")
    assert isinstance(geom, data.TimeInterval)
    assert geom.coordinates == [0, 1]


def test_load_timeinterval_from_dict():
    """Test that a TimeInterval can be loaded from a dictionary."""
    obj = {"type": "TimeInterval", "coordinates": [0, 1]}
    geom = data.geometry_validate(obj, mode="dict")
    assert isinstance(geom, data.TimeInterval)
    assert geom.coordinates == [0, 1]


def test_load_timeinterval_from_attributes():
    """Test that a TimeInterval can be loaded from attributes."""
    obj = data.TimeInterval(coordinates=[0, 1])
    geom = data.geometry_validate(obj, mode="attributes")
    assert isinstance(geom, data.TimeInterval)
    assert geom.coordinates == [0, 1]


def test_load_point_from_json():
    """Test that a Point can be loaded from JSON."""
    obj = json.dumps({"type": "Point", "coordinates": [0, 1]})
    geom = data.geometry_validate(obj, mode="json")
    assert isinstance(geom, data.Point)
    assert geom.coordinates == [0, 1]


def test_load_point_from_dict():
    """Test that a Point can be loaded from a dictionary."""
    obj = {"type": "Point", "coordinates": [0, 1]}
    geom = data.geometry_validate(obj, mode="dict")
    assert isinstance(geom, data.Point)
    assert geom.coordinates == [0, 1]


def test_load_point_from_attributes():
    """Test that a Point can be loaded from attributes."""
    obj = data.Point(coordinates=[0, 1])
    geom = data.geometry_validate(obj, mode="attributes")
    assert isinstance(geom, data.Point)
    assert geom.coordinates == [0, 1]


def test_load_linestring_from_json():
    """Test that a LineString can be loaded from JSON."""
    obj = json.dumps({"type": "LineString", "coordinates": [[0, 1], [2, 3]]})
    geom = data.geometry_validate(obj, mode="json")
    assert isinstance(geom, data.LineString)
    assert geom.coordinates == [[0, 1], [2, 3]]


def test_load_linestring_from_dict():
    """Test that a LineString can be loaded from a dictionary."""
    obj = {"type": "LineString", "coordinates": [[0, 1], [2, 3]]}
    geom = data.geometry_validate(obj, mode="dict")
    assert isinstance(geom, data.LineString)
    assert geom.coordinates == [[0, 1], [2, 3]]


def test_load_linestring_from_attributes():
    """Test that a LineString can be loaded from attributes."""
    obj = data.LineString(coordinates=[[0, 1], [2, 3]])
    geom = data.geometry_validate(obj, mode="attributes")
    assert isinstance(geom, data.LineString)
    assert geom.coordinates == [[0, 1], [2, 3]]


def test_load_polygon_from_json():
    """Test that a Polygon can be loaded from JSON."""
    obj = json.dumps(
        {"type": "Polygon", "coordinates": [[[0, 1], [2, 3], [4, 5], [0, 1]]]}
    )
    geom = data.geometry_validate(obj, mode="json")
    assert isinstance(geom, data.Polygon)
    assert geom.coordinates == [[[0, 1], [2, 3], [4, 5], [0, 1]]]


def test_load_polygon_from_dict():
    """Test that a Polygon can be loaded from a dictionary."""
    obj = {
        "type": "Polygon",
        "coordinates": [[[0, 1], [2, 3], [4, 5], [0, 1]]],
    }
    geom = data.geometry_validate(obj, mode="dict")
    assert isinstance(geom, data.Polygon)
    assert geom.coordinates == [[[0, 1], [2, 3], [4, 5], [0, 1]]]


def test_load_polygon_from_attributes():
    """Test that a Polygon can be loaded from attributes."""
    obj = data.Polygon(coordinates=[[[0, 1], [2, 3], [4, 5], [0, 1]]])
    geom = data.geometry_validate(obj, mode="attributes")
    assert isinstance(geom, data.Polygon)
    assert geom.coordinates == [[[0, 1], [2, 3], [4, 5], [0, 1]]]


def test_load_multipoint_from_json():
    """Test that a MultiPoint can be loaded from JSON."""
    obj = json.dumps({"type": "MultiPoint", "coordinates": [[0, 1], [2, 3]]})
    geom = data.geometry_validate(obj, mode="json")
    assert isinstance(geom, data.MultiPoint)
    assert geom.coordinates == [[0, 1], [2, 3]]


def test_load_multipoint_from_dict():
    """Test that a MultiPoint can be loaded from a dictionary."""
    obj = {"type": "MultiPoint", "coordinates": [[0, 1], [2, 3]]}
    geom = data.geometry_validate(obj, mode="dict")
    assert isinstance(geom, data.MultiPoint)
    assert geom.coordinates == [[0, 1], [2, 3]]


def test_load_multipoint_from_attributes():
    """Test that a MultiPoint can be loaded from attributes."""
    obj = data.MultiPoint(coordinates=[[0, 1], [2, 3]])
    geom = data.geometry_validate(obj, mode="attributes")
    assert isinstance(geom, data.MultiPoint)
    assert geom.coordinates == [[0, 1], [2, 3]]


def test_load_multilinestring_from_json():
    """Test that a MultiLineString can be loaded from JSON."""
    obj = json.dumps(
        {
            "type": "MultiLineString",
            "coordinates": [[[0, 1], [2, 3]], [[4, 5], [6, 7]]],
        }
    )
    geom = data.geometry_validate(obj, mode="json")
    assert isinstance(geom, data.MultiLineString)
    assert geom.coordinates == [[[0, 1], [2, 3]], [[4, 5], [6, 7]]]


def test_load_multilinestring_from_dict():
    """Test that a MultiLineString can be loaded from a dictionary."""
    obj = {
        "type": "MultiLineString",
        "coordinates": [[[0, 1], [2, 3]], [[4, 5], [6, 7]]],
    }
    geom = data.geometry_validate(obj, mode="dict")
    assert isinstance(geom, data.MultiLineString)
    assert geom.coordinates == [[[0, 1], [2, 3]], [[4, 5], [6, 7]]]


def test_load_multilinestring_from_attributes():
    """Test that a MultiLineString can be loaded from attributes."""
    obj = data.MultiLineString(
        coordinates=[[[0, 1], [2, 3]], [[4, 5], [6, 7]]]
    )
    geom = data.geometry_validate(obj, mode="attributes")
    assert isinstance(geom, data.MultiLineString)
    assert geom.coordinates == [[[0, 1], [2, 3]], [[4, 5], [6, 7]]]


def test_load_multipolygon_from_json():
    """Test that a MultiPolygon can be loaded from JSON."""
    obj = json.dumps(
        {
            "type": "MultiPolygon",
            "coordinates": [[[[0, 1], [2, 3], [4, 5], [0, 1]]]],
        }
    )
    geom = data.geometry_validate(obj, mode="json")
    assert isinstance(geom, data.MultiPolygon)
    assert geom.coordinates == [[[[0, 1], [2, 3], [4, 5], [0, 1]]]]


def test_load_multipolygon_from_dict():
    """Test that a MultiPolygon can be loaded from a dictionary."""
    obj = {
        "type": "MultiPolygon",
        "coordinates": [[[[0, 1], [2, 3], [4, 5], [0, 1]]]],
    }
    geom = data.geometry_validate(obj, mode="dict")
    assert isinstance(geom, data.MultiPolygon)
    assert geom.coordinates == [[[[0, 1], [2, 3], [4, 5], [0, 1]]]]


def test_load_multipolygon_from_attributes():
    """Test that a MultiPolygon can be loaded from attributes."""
    obj = data.MultiPolygon(coordinates=[[[[0, 1], [2, 3], [4, 5], [0, 1]]]])
    geom = data.geometry_validate(obj, mode="attributes")
    assert isinstance(geom, data.MultiPolygon)
    assert geom.coordinates == [[[[0, 1], [2, 3], [4, 5], [0, 1]]]]


def test_geometry_validate_fails_if_no_geometry_type_in_dict():
    """Test that geometry_validate fails if no geometry type is in the dict."""
    obj = {"coordinates": [[[0, 1], [2, 3], [4, 5], [0, 1]]]}
    with pytest.raises(ValueError):
        data.geometry_validate(obj, mode="dict")


def test_geometry_validate_fails_if_no_geometry_type_in_attributes():
    """Test geometry_validate fails if no geometry type is provided."""

    @dataclass
    class NoType:
        coordinates: List[float]

    obj = NoType(coordinates=[0, 1, 2, 3])
    with pytest.raises(ValueError):
        data.geometry_validate(obj, mode="attributes")


def test_geometry_validate_fails_with_unknown_geometry_type():
    """Test that geometry_validate fails with an unknown geometry type."""
    obj = {
        "type": "Unknown",
        "coordinates": [[[0, 1], [2, 3], [4, 5], [0, 1]]],
    }
    with pytest.raises(ValueError):
        data.geometry_validate(obj, mode="dict")


def test_geometry_validate_fails_with_invalid_geometry():
    """Test that geometry_validate fails with an invalid geometry."""
    obj = {"type": "Point", "coordinates": [0, 1, 2]}
    with pytest.raises(ValueError):
        data.geometry_validate(obj, mode="dict")


def test_time_interval_sorts_start_end():
    """TimeInterval auto-sorts [start, end] when start > end."""
    geom = data.TimeInterval(coordinates=[2, 1])
    assert geom.coordinates == [1, 2]


def test_fixes_invalid_bbox():
    box = data.BoundingBox(coordinates=[1, 0, 0, 1])
    assert box.coordinates == [0, 0, 1, 1]

    box = data.BoundingBox(coordinates=[0, 1, 1, 0])
    assert box.coordinates == [0, 0, 1, 1]

    box = data.BoundingBox(coordinates=[1, 1, 0, 0])
    assert box.coordinates == [0, 0, 1, 1]


def test_invalid_linestring():
    """Test that an invalid linestring fails."""
    # Has to have at least two points
    with pytest.raises(ValueError):
        data.LineString(coordinates=[[0, 1]])


def test_invalid_multipoint():
    # Has to have at least one point
    with pytest.raises(ValueError):
        data.MultiPoint(coordinates=[])


def test_invalid_polygon():
    # Has to have at least one ring
    with pytest.raises(ValueError):
        data.Polygon(coordinates=[])

    # Has to have at least three points
    with pytest.raises(ValueError):
        data.Polygon(coordinates=[[[0, 1], [2, 3]]])

    # Rings need to have at least three points
    with pytest.raises(ValueError):
        data.Polygon(coordinates=[[[0, 1], [2, 3], [4, 0]], [[1, 1], [1, 2]]])


def test_invalid_multiline():
    # Has to have at least one linestring
    with pytest.raises(ValueError):
        data.LineString(coordinates=[])


def test_fixes_linestring_order():
    linestring = data.LineString(coordinates=[[1, 1], [0.5, 1], [0, 1]])
    assert linestring.coordinates == [[0, 1], [0.5, 1], [1, 1]]
