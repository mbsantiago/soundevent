"""Test Suite for geometric operations."""
import math
from typing import List

import pytest

from soundevent import data
from soundevent.data.geometries import BaseGeometry
from soundevent.geometry.operations import buffer_geometry, compute_bounds


def test_compute_timestamp_bounds():
    """Test that compute_bounds works with TimeStamp geometries."""
    geom = data.TimeStamp(coordinates=2)
    bounds = compute_bounds(geom)
    assert bounds == (2, 0, 2, data.MAX_FREQUENCY)


def test_compute_timeinterval_bounds():
    """Test that compute_bounds works with TimeInterval geometries."""
    geom = data.TimeInterval(coordinates=[1, 2])
    bounds = compute_bounds(geom)
    assert bounds == (1, 0, 2, data.MAX_FREQUENCY)


def test_compute_bounding_box_bounds():
    """Test that compute_bounds works with BoundingBox geometries."""
    geom = data.BoundingBox(coordinates=[1, 2, 3, 4])
    bounds = compute_bounds(geom)
    assert bounds == (1, 2, 3, 4)


def test_compute_point_bounds():
    """Test that compute_bounds works with Point geometries."""
    geom = data.Point(coordinates=[1, 2])
    bounds = compute_bounds(geom)
    assert bounds == (1, 2, 1, 2)


def test_compute_linestring_bounds():
    """Test that compute_bounds works with LineString geometries."""
    geom = data.LineString(coordinates=[[1, 2], [3, 4]])
    bounds = compute_bounds(geom)
    assert bounds == (1, 2, 3, 4)


def test_compute_polygon_bounds():
    """Test that compute_bounds works with Polygon geometries."""
    geom = data.Polygon(coordinates=[[[1, 2], [3, 4], [5, 6], [1, 2]]])
    bounds = compute_bounds(geom)
    assert bounds == (1, 2, 5, 6)


def test_buffer_geometry_fails_with_non_positive_buffers():
    """Test that buffer_geometry fails with non-positive buffers."""
    with pytest.raises(ValueError):
        buffer_geometry(
            geometry=data.TimeInterval(coordinates=[0, 1]),
            time_buffer=-1,
        )

    with pytest.raises(ValueError):
        buffer_geometry(
            geometry=data.TimeInterval(coordinates=[0, 1]),
            freq_buffer=-1,
        )


def test_buffer_geometry_fails_with_unexpected_geometry():
    """Test that buffer_geometry fails with unexpected geometry."""

    class UnexpectedGeometry(BaseGeometry):
        coordinates: List[float]
        type: str = "unexpected"  # type: ignore

    geom = UnexpectedGeometry(coordinates=[0, 1])

    with pytest.raises(NotImplementedError):
        buffer_geometry(geometry=geom)  # type: ignore


def test_buffer_timestamp_geometry():
    """Test that buffer_geometry works with TimeStamp geometries."""
    geom = data.TimeStamp(coordinates=2)
    buffered_geom = buffer_geometry(geom, time_buffer=1)
    assert buffered_geom == data.TimeInterval(coordinates=[1, 3])


def test_buffer_timeinterval_geometry():
    """Test that buffer_geometry works with TimeInterval geometries."""
    geom = data.TimeInterval(coordinates=[1, 2])
    buffered_geom = buffer_geometry(geom, time_buffer=1)
    assert buffered_geom == data.TimeInterval(coordinates=[0, 3])


def test_buffer_boundingbox_geometry_in_freq_axis():
    """Test buffer_geometry works with BoundingBox in the frequency axis."""
    geom = data.BoundingBox(coordinates=[1, 2, 3, 4])
    buffered_geom = buffer_geometry(geom, freq_buffer=1)
    assert buffered_geom == data.BoundingBox(coordinates=[1, 1, 3, 5])


def test_buffer_boundingbox_geometry_in_time_axis():
    """Test buffer_geometry works with BoundingBox in the time axis."""
    geom = data.BoundingBox(coordinates=[1, 2, 3, 4])
    buffered_geom = buffer_geometry(geom, time_buffer=1)
    assert buffered_geom == data.BoundingBox(coordinates=[0, 2, 4, 4])


def test_buffered_geometry_time_is_not_negative():
    """Test that buffer_geometry fails when time buffer is negative."""
    geom = data.TimeInterval(coordinates=[1, 2])
    buffered = buffer_geometry(geom, time_buffer=2)
    assert buffered == data.TimeInterval(coordinates=[0, 4])


def test_buffered_geometry_freq_is_not_negative():
    """Test that buffer_geometry fails when frequency buffer is negative."""
    geom = data.BoundingBox(coordinates=[1, 2, 3, 4])
    buffered = buffer_geometry(geom, freq_buffer=2)
    assert buffered == data.BoundingBox(coordinates=[1, 0, 3, 6])


def test_buffer_polygon_geometry_in_time_axis():
    """Test that buffer_geometry works with Polygon geometries."""
    geom = data.Polygon(coordinates=[[[1, 2], [4, 3], [5, 6], [1, 2]]])
    buffered_geom = buffer_geometry(geom, time_buffer=1)
    bounds = compute_bounds(buffered_geom)
    assert math.isclose(bounds[0], 0, rel_tol=1e-6)
    assert math.isclose(bounds[1], 2, rel_tol=1e-6)
    assert math.isclose(bounds[2], 6, rel_tol=1e-6)
    assert math.isclose(bounds[3], 6, rel_tol=1e-6)


def test_buffer_polygon_geometry_in_freq_axis():
    """Test that buffer_geometry works with Polygon geometries."""
    geom = data.Polygon(coordinates=[[[1, 2], [4, 3], [5, 6], [1, 2]]])
    buffered_geom = buffer_geometry(geom, freq_buffer=1)
    bounds = compute_bounds(buffered_geom)
    assert math.isclose(bounds[0], 1, rel_tol=1e-6)
    assert math.isclose(bounds[1], 1, rel_tol=1e-6)
    assert math.isclose(bounds[2], 5, rel_tol=1e-6)
    assert math.isclose(bounds[3], 7, rel_tol=1e-6)
