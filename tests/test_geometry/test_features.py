"""Test suite for functions computing the geometric features."""

import pytest

from soundevent import terms
from soundevent.data import geometries
from soundevent.geometry import compute_geometric_features


def test_compute_time_stamp_features():
    """Test that the duration of a TimeStamp is 0."""
    time_stamp = geometries.TimeStamp(coordinates=0)
    features = compute_geometric_features(time_stamp)
    assert len(features) == 1
    assert features[0].term == terms.duration
    assert features[0].value == 0


def test_compute_time_interval_features():
    """Test that the duration of a TimeInterval is correct."""
    time_interval = geometries.TimeInterval(coordinates=[0, 1])
    features = compute_geometric_features(time_interval)
    assert len(features) == 1
    assert features[0].term == terms.duration
    assert features[0].value == 1


def test_compute_bounding_box_features():
    """Test that the duration of a BoundingBox is correct."""
    bounding_box = geometries.BoundingBox(coordinates=[0, 1, 2, 3])
    features = compute_geometric_features(bounding_box)
    assert len(features) == 4
    assert features[0].term == terms.duration
    assert features[0].value == 2
    assert features[1].term == terms.low_freq
    assert features[1].value == 1
    assert features[2].term == terms.high_freq
    assert features[2].value == 3
    assert features[3].term == terms.bandwidth
    assert features[3].value == 2


def test_compute_point_features():
    """Test that the duration of a Point is 0."""
    point = geometries.Point(coordinates=[0, 1])
    features = compute_geometric_features(point)
    assert len(features) == 4
    assert features[0].term == terms.duration
    assert features[0].value == 0
    assert features[1].term == terms.low_freq
    assert features[1].value == 1
    assert features[2].term == terms.high_freq
    assert features[2].value == 1
    assert features[3].term == terms.bandwidth
    assert features[3].value == 0


def test_compute_linestring_features():
    """Test that the duration of a LineString is correct."""
    linestring = geometries.LineString(coordinates=[[1, 2], [4, 3]])
    features = compute_geometric_features(linestring)
    assert len(features) == 4
    assert features[0].term == terms.duration
    assert features[0].value == 3
    assert features[1].term == terms.low_freq
    assert features[1].value == 2
    assert features[2].term == terms.high_freq
    assert features[2].value == 3
    assert features[3].term == terms.bandwidth
    assert features[3].value == 1


def test_compute_polygon_features():
    """Test that the duration of a Polygon is correct."""
    polygon = geometries.Polygon(coordinates=[[[1, 2], [4, 3], [5, 0]]])
    features = compute_geometric_features(polygon)
    assert len(features) == 4
    assert features[0].term == terms.duration
    assert features[0].value == 4
    assert features[1].term == terms.low_freq
    assert features[1].value == 0
    assert features[2].term == terms.high_freq
    assert features[2].value == 3
    assert features[3].term == terms.bandwidth
    assert features[3].value == 3


def test_compute_multipoint_features():
    """Test that the duration of a MultiPoint is correct."""
    multipoint = geometries.MultiPoint(coordinates=[[1, 2], [4, 3]])
    features = compute_geometric_features(multipoint)
    assert len(features) == 5
    assert features[0].term == terms.duration
    assert features[0].value == 3
    assert features[1].term == terms.low_freq
    assert features[1].value == 2
    assert features[2].term == terms.high_freq
    assert features[2].value == 3
    assert features[3].term == terms.bandwidth
    assert features[3].value == 1
    assert features[4].term == terms.num_segments
    assert features[4].value == 2


def test_compute_multilinestring_features():
    """Test that the duration of a MultiLineString is correct."""
    multilinestring = geometries.MultiLineString(
        coordinates=[[[1, 2], [4, 3]], [[2, 1], [5, 2]]]
    )
    features = compute_geometric_features(multilinestring)
    assert len(features) == 5
    assert features[0].term == terms.duration
    assert features[0].value == 4
    assert features[1].term == terms.low_freq
    assert features[1].value == 1
    assert features[2].term == terms.high_freq
    assert features[2].value == 3
    assert features[3].term == terms.bandwidth
    assert features[3].value == 2
    assert features[4].term == terms.num_segments
    assert features[4].value == 2


def test_compute_multipolygon_features():
    """Test that the duration of a MultiPolygon is correct."""
    multipolygon = geometries.MultiPolygon(
        coordinates=[[[[0, 2], [4, 3], [5, 0]]], [[[1, 3], [2, 5], [5, 2]]]]
    )
    features = compute_geometric_features(multipolygon)
    assert len(features) == 5
    assert features[0].term == terms.duration
    assert features[0].value == 5
    assert features[1].term == terms.low_freq
    assert features[1].value == 0
    assert features[2].term == terms.high_freq
    assert features[2].value == 5
    assert features[3].term == terms.bandwidth
    assert features[3].value == 5
    assert features[4].term == terms.num_segments
    assert features[4].value == 2


def test_compute_geometry_features_fails_on_unrecognized_geometry():
    """Test that an error is raised when an unrecognized geometry is passed."""

    class UnrecognizedGeometry(geometries.BaseGeometry):
        type: str = "unrecognized"

        coordinates: list

    geometry = UnrecognizedGeometry(coordinates=[0, 1, 2, 3])
    with pytest.raises(NotImplementedError):
        compute_geometric_features(geometry)  # type: ignore
