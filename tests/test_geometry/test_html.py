"""Test that geometries get converted to HTML."""

import html5lib

from soundevent import data
from soundevent.geometry.html import geometry_to_html


def test_can_generate_time_stamp_html(time_stamp: data.TimeStamp) -> None:
    """Test that a time stamp can be converted to HTML."""
    html = geometry_to_html(time_stamp)
    html5lib.parse(html)


def test_can_generate_time_interval_html(
    time_interval: data.TimeInterval,
) -> None:
    """Test that a time interval can be converted to HTML."""
    html = geometry_to_html(time_interval)
    html5lib.parse(html)


def test_can_generate_point_html(point: data.Point) -> None:
    """Test that a point can be converted to HTML."""
    html = geometry_to_html(point)
    html5lib.parse(html)


def test_can_generate_linestring_html(linestring: data.LineString) -> None:
    """Test that a line string can be converted to HTML."""
    html = geometry_to_html(linestring)
    html5lib.parse(html)


def test_can_generate_bounding_box_html(
    bounding_box: data.BoundingBox,
) -> None:
    """Test that a bounding box can be converted to HTML."""
    html = geometry_to_html(bounding_box)
    html5lib.parse(html)


def test_can_generate_polygon_html(polygon: data.Polygon) -> None:
    """Test that a polygon can be converted to HTML."""
    html = geometry_to_html(polygon)
    html5lib.parse(html)


def test_can_generate_multi_point_html(multi_point: data.MultiPoint) -> None:
    """Test that a multi point can be converted to HTML."""
    html = geometry_to_html(multi_point)
    html5lib.parse(html)


def test_can_generate_multi_line_string_html(
    multi_line_string: data.MultiLineString,
) -> None:
    """Test that a multi line string can be converted to HTML."""
    html = geometry_to_html(multi_line_string)
    html5lib.parse(html)


def test_can_generate_multi_polygon_html(
    multi_polygon: data.MultiPolygon,
) -> None:
    """Test that a multi polygon can be converted to HTML."""
    html = geometry_to_html(multi_polygon)
    html5lib.parse(html)
