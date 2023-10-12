"""Test Suite for geometry conversion functions."""

import shapely

from soundevent import data, geometry


def test_timestamp_is_converted_to_shapely():
    """Test that a timestamp is converted to a Shapely Point."""
    timestamp = data.TimeStamp(coordinates=1)
    geom = geometry.geometry_to_shapely(timestamp)
    assert isinstance(geom, shapely.Geometry)


def test_timeinterval_is_converted_to_shapely():
    """Test that a time interval is converted to a Shapely LineString."""
    timeinterval = data.TimeInterval(coordinates=[1, 2])
    geom = geometry.geometry_to_shapely(timeinterval)
    assert isinstance(geom, shapely.Geometry)


def test_bounding_box_is_converted_to_shapely():
    """Test that a bounding box is converted to a Shapely Polygon."""
    bounding_box = data.BoundingBox(coordinates=[1, 2, 3, 4])
    geom = geometry.geometry_to_shapely(bounding_box)
    assert isinstance(geom, shapely.Geometry)
    assert geom.geom_type == "Polygon"
    assert tuple(bounding_box.coordinates) == geom.bounds


def test_point_is_converted_to_shapely():
    """Test that a point is converted to a Shapely Point."""
    point = data.Point(coordinates=[1, 2])
    geom = geometry.geometry_to_shapely(point)
    assert isinstance(geom, shapely.Geometry)
    assert geom.geom_type == "Point"
    assert point.model_dump_json() == shapely.to_geojson(geom)


def test_linestring_is_converted_to_shapely():
    """Test that a linestring is converted to a Shapely LineString."""
    linestring = data.LineString(coordinates=[[1, 2], [3, 4]])
    geom = geometry.geometry_to_shapely(linestring)
    assert isinstance(geom, shapely.Geometry)
    assert geom.geom_type == "LineString"
    assert linestring.model_dump_json() == shapely.to_geojson(geom)


def test_polygon_is_converted_to_shapely():
    """Test that a polygon is converted to a Shapely Polygon."""
    polygon = data.Polygon(coordinates=[[[1, 2], [3, 4], [5, 6], [1, 2]]])
    geom = geometry.geometry_to_shapely(polygon)
    assert isinstance(geom, shapely.Geometry)
    assert geom.geom_type == "Polygon"
    assert polygon.model_dump_json() == shapely.to_geojson(geom)


def test_multipoint_is_converted_to_shapely():
    """Test that a multipoint is converted to a Shapely MultiPoint."""
    multipoint = data.MultiPoint(coordinates=[[1, 2], [3, 4]])
    geom = geometry.geometry_to_shapely(multipoint)
    assert isinstance(geom, shapely.Geometry)
    assert geom.geom_type == "MultiPoint"
    assert multipoint.model_dump_json() == shapely.to_geojson(geom)


def test_multilinestring_is_converted_to_shapely():
    """Test that a multilinestring is converted to a Shapely geometry."""
    multilinestring = data.MultiLineString(
        coordinates=[[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
    )
    geom = geometry.geometry_to_shapely(multilinestring)
    assert isinstance(geom, shapely.Geometry)
    assert geom.geom_type == "MultiLineString"
    assert multilinestring.model_dump_json() == shapely.to_geojson(geom)


def test_multipolygon_is_converted_to_shapely():
    """Test that a multipolygon is converted to a Shapely MultiPolygon."""
    multipolygon = data.MultiPolygon(
        coordinates=[
            [[[1, 2], [3, 4], [5, 6], [1, 2]]],
            [[[7, 8], [9, 10], [11, 12], [7, 8]]],
        ]
    )
    geom = geometry.geometry_to_shapely(multipolygon)
    assert isinstance(geom, shapely.Geometry)
    assert geom.geom_type == "MultiPolygon"
    assert multipolygon.model_dump_json() == shapely.to_geojson(geom)
