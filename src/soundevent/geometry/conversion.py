"""Convert Geometry objects into shapely objects and vice versa."""

from typing import overload

import shapely
from shapely import geometry

from soundevent import data

__all__ = [
    "geometry_to_shapely",
]


def time_stamp_to_shapely(geom: data.TimeStamp) -> shapely.LineString:
    """Convert a TimeStamp to a shapely geometry.

    Parameters
    ----------
    geom
        The TimeStamp geometry to convert.

    Returns
    -------
    shapely.Geometry
        The converted shapely geometry.
    """
    return shapely.linestrings(
        [
            [geom.coordinates, 0],
            [geom.coordinates, data.MAX_FREQUENCY],
        ]
    )


def time_interval_to_shapely(geom: data.TimeInterval) -> shapely.Polygon:
    """Convert a TimeInterval to a shapely geometry.

    Parameters
    ----------
    geom
        The TimeInterval geometry to convert.

    Returns
    -------
    shapely.Geometry
        The converted shapely geometry.
    """
    start_time, end_time = geom.coordinates
    return geometry.box(
        start_time,
        0,
        end_time,
        data.MAX_FREQUENCY,
    )


def point_to_shapely(geom: data.Point) -> shapely.Point:
    """Convert a Point to a shapely geometry.

    Parameters
    ----------
    geom
        The Point geometry to convert.

    Returns
    -------
    shapely.Point
        The converted shapely geometry.
    """
    return geometry.Point(geom.coordinates)


def linestring_to_shapely(geom: data.LineString) -> shapely.LineString:
    """Convert a LineString to a shapely geometry.

    Parameters
    ----------
    geom
        The LineString geometry to convert.

    Returns
    -------
    shapely.LineString
        The converted shapely geometry.
    """
    return geometry.LineString(geom.coordinates)


def polygon_to_shapely(geom: data.Polygon) -> shapely.Polygon:
    """Convert a Polygon to a shapely geometry.

    Parameters
    ----------
    geom
        The Polygon geometry to convert.

    Returns
    -------
    shapely.Polygon
        The converted shapely geometry.
    """
    shell = geom.coordinates[0]
    holes = geom.coordinates[1:]
    return geometry.Polygon(shell, holes)


def bounding_box_to_shapely(geom: data.BoundingBox) -> shapely.Polygon:
    """Convert a BoundingBox to a shapely geometry.

    Parameters
    ----------
    geom
        The BoundingBox geometry to convert.

    Returns
    -------
    shapely.Polygon
        The converted shapely geometry.
    """
    start_time, low_freq, end_time, high_freq = geom.coordinates
    return geometry.box(
        start_time,
        low_freq,
        end_time,
        high_freq,
    )


def multipoint_to_shapely(geom: data.MultiPoint) -> shapely.MultiPoint:
    """Convert a MultiPoint to a shapely geometry.

    Parameters
    ----------
    geom
        The MultiPoint geometry to convert.

    Returns
    -------
    shapely.MultiPoint
        The converted shapely geometry.
    """
    return geometry.MultiPoint(geom.coordinates)


def multilinestring_to_shapely(
    geom: data.MultiLineString,
) -> shapely.MultiLineString:
    """Convert a MultiLineString to a shapely geometry.

    Parameters
    ----------
    geom
        The MultiLineString geometry to convert.

    Returns
    -------
    shapely.MultiLineString
        The converted shapely geometry.
    """
    return geometry.MultiLineString(geom.coordinates)


def multipolygon_to_shapely(
    geom: data.MultiPolygon,
) -> shapely.MultiPolygon:
    """Convert a MultiPolygon to a shapely geometry.

    Parameters
    ----------
    geom
        The MultiPolygon geometry to convert.

    Returns
    -------
    shapely.MultiPolygon
        The converted shapely geometry.
    """
    polgons = []
    for poly in geom.coordinates:
        shell = poly[0]
        holes = poly[1:]
        polygon = geometry.Polygon(shell, holes)
        polgons.append(polygon)
    return geometry.MultiPolygon(polgons)


@overload
def geometry_to_shapely(
    geom: data.TimeStamp,
) -> shapely.LineString: ...


@overload
def geometry_to_shapely(
    geom: data.TimeInterval,
) -> shapely.Polygon: ...


@overload
def geometry_to_shapely(
    geom: data.Point,
) -> shapely.Point: ...


@overload
def geometry_to_shapely(
    geom: data.LineString,
) -> shapely.LineString: ...


@overload
def geometry_to_shapely(
    geom: data.Polygon,
) -> shapely.Polygon: ...


@overload
def geometry_to_shapely(
    geom: data.BoundingBox,
) -> shapely.Polygon: ...


@overload
def geometry_to_shapely(
    geom: data.MultiPoint,
) -> shapely.MultiPoint: ...


@overload
def geometry_to_shapely(
    geom: data.MultiLineString,
) -> shapely.MultiLineString: ...


@overload
def geometry_to_shapely(
    geom: data.MultiPolygon,
) -> shapely.MultiPolygon: ...


def geometry_to_shapely(
    geom: data.Geometry,
) -> shapely.Geometry:
    """Convert a Geometry to a shapely geometry.

    Parameters
    ----------
    geom
        The Geometry to convert.

    Returns
    -------
    shapely.Geometry
        The converted shapely geometry.
    """
    if geom.type == "TimeStamp":
        return time_stamp_to_shapely(geom)
    if geom.type == "TimeInterval":
        return time_interval_to_shapely(geom)
    if geom.type == "Point":
        return point_to_shapely(geom)
    if geom.type == "LineString":
        return linestring_to_shapely(geom)
    if geom.type == "Polygon":
        return polygon_to_shapely(geom)
    if geom.type == "BoundingBox":
        return bounding_box_to_shapely(geom)
    if geom.type == "MultiPoint":
        return multipoint_to_shapely(geom)
    if geom.type == "MultiLineString":
        return multilinestring_to_shapely(geom)
    if geom.type == "MultiPolygon":
        return multipolygon_to_shapely(geom)

    raise NotImplementedError(f"Unknown geometry type: {geom.type}")
