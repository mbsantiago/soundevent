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


def test_shapely_point_is_converted_to_point():
    """Test that a Shapely Point is converted to a Point."""
    # Given
    point = data.Point(coordinates=[1, 2])
    shapely_geom = geometry.geometry_to_shapely(point)

    # When
    converted_point = geometry.shapely_to_geometry(shapely_geom)

    # Then
    assert isinstance(converted_point, data.Point)
    assert converted_point == point


def test_shapely_linestring_is_converted_to_linestring():
    """Test that a Shapely LineString is converted to a LineString."""
    # Given
    linestring = data.LineString(coordinates=[[1, 2], [3, 4]])
    shapely_geom = geometry.geometry_to_shapely(linestring)

    # When
    converted_linestring = geometry.shapely_to_geometry(shapely_geom)

    # Then
    assert isinstance(converted_linestring, data.LineString)
    assert converted_linestring == linestring


def test_shapely_polygon_is_converted_to_polygon():
    """Test that a Shapely Polygon is converted to a Polygon."""
    # Given
    polygon = data.Polygon(coordinates=[[[1, 2], [3, 4], [5, 6], [1, 2]]])
    shapely_geom = geometry.geometry_to_shapely(polygon)

    # When
    converted_polygon = geometry.shapely_to_geometry(shapely_geom)

    # Then
    assert isinstance(converted_polygon, data.Polygon)
    assert converted_polygon == polygon


def test_shapely_polygon_with_hole_is_converted_to_polygon():
    """Test that a Shapely Polygon with a hole is converted to a Polygon."""
    # Given
    polygon = data.Polygon(
        coordinates=[
            [[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
            [[2, 2], [2, 8], [8, 8], [8, 2], [2, 2]],
        ]
    )
    shapely_geom = geometry.geometry_to_shapely(polygon)

    # When
    converted_polygon = geometry.shapely_to_geometry(shapely_geom)

    # Then
    assert isinstance(converted_polygon, data.Polygon)
    assert converted_polygon == polygon


def test_shapely_multipoint_is_converted_to_multipoint():
    """Test that a Shapely MultiPoint is converted to a MultiPoint."""
    # Given
    multipoint = data.MultiPoint(coordinates=[[1, 2], [3, 4]])
    shapely_geom = geometry.geometry_to_shapely(multipoint)

    # When
    converted_multipoint = geometry.shapely_to_geometry(shapely_geom)

    # Then
    assert isinstance(converted_multipoint, data.MultiPoint)
    assert converted_multipoint == multipoint


def test_shapely_multilinestring_is_converted_to_multilinestring():
    """Test that a Shapely MultiLineString is converted to a MultiLineString."""
    # Given
    multilinestring = data.MultiLineString(
        coordinates=[[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
    )
    shapely_geom = geometry.geometry_to_shapely(multilinestring)

    # When
    converted_multilinestring = geometry.shapely_to_geometry(shapely_geom)

    # Then
    assert isinstance(converted_multilinestring, data.MultiLineString)
    assert converted_multilinestring == multilinestring


def test_shapely_multipolygon_is_converted_to_multipolygon():
    """Test that a Shapely MultiPolygon is converted to a MultiPolygon."""
    # Given
    multipolygon = data.MultiPolygon(
        coordinates=[
            [[[1, 2], [3, 4], [5, 6], [1, 2]]],
            [[[7, 8], [9, 10], [11, 12], [7, 8]]],
        ]
    )
    shapely_geom = geometry.geometry_to_shapely(multipolygon)

    # When
    converted_multipolygon = geometry.shapely_to_geometry(shapely_geom)

    # Then
    assert isinstance(converted_multipolygon, data.MultiPolygon)
    assert converted_multipolygon == multipolygon
