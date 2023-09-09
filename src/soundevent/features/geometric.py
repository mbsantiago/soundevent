"""Compute sound event features from geometries.

This module contains functions to compute sound event features from their
geometries. These are simple yet useful features that provide a first glance of
the sound event.

These features are directly computed from the geometry, and do not depend on
the audio signal nor the spectrogram.

The computed features are:

- ``duration``: The duration of the sound event, in seconds.
- ``low_freq``: The lowest frequency of the sound event, in Hz.
- ``high_freq``: The highest frequency of the sound event, in Hz.
- ``bandwidth``: The bandwidth of the sound event, in Hz.
- ``num_segments``: The number of segments of the sound event.

Some of these features are not applicable to all geometries, as they require
information not present in the geometry. However the function
``compute_geometric_features`` will compute all the features that are
applicable to the given geometry and return them in a list.

Examples
--------
To compute the features of a bounding box:

>>> from soundevent import data, features
>>> geometry = data.BoundingBox(
...     coordinates=(0, 0, 1, 1000),
... )
>>> features.compute_geometric_features(geometry)
[Feature(name='duration', value=1),
    Feature(name='low_freq', value=0),
    Feature(name='high_freq', value=1000),
    Feature(name='bandwidth', value=1000)]
"""
from typing import Any, Callable, Dict, List

from soundevent.data import Feature, geometries

__all__ = [
    "compute_geometric_features",
]


DURATION = "duration"
LOW_FREQ = "low_freq"
HIGH_FREQ = "high_freq"
BANDWIDTH = "bandwidth"
NUM_SEGMENTS = "num_segments"


def _compute_time_stamp_features(
    _: geometries.TimeStamp,
) -> List[Feature]:
    return [Feature(name=DURATION, value=0)]


def _compute_time_interval_features(
    geometry: geometries.TimeInterval,
) -> List[Feature]:
    start, end = geometry.coordinates
    return [Feature(name=DURATION, value=end - start)]


def _compute_bounding_box_features(
    geometry: geometries.BoundingBox,
) -> List[Feature]:
    start_time, low_freq, end_time, high_freq = geometry.coordinates
    return [
        Feature(name=DURATION, value=end_time - start_time),
        Feature(name=LOW_FREQ, value=low_freq),
        Feature(name=HIGH_FREQ, value=high_freq),
        Feature(name=BANDWIDTH, value=high_freq - low_freq),
    ]


def _compute_point_features(
    geometry: geometries.Point,
) -> List[Feature]:
    _, low_freq, _, high_freq = geometry.bounds

    return [
        Feature(name=DURATION, value=0),
        Feature(name=LOW_FREQ, value=low_freq),
        Feature(name=HIGH_FREQ, value=high_freq),
        Feature(name=BANDWIDTH, value=0),
    ]


def _compute_line_string_features(
    geometry: geometries.LineString,
) -> List[Feature]:
    start_time, low_freq, end_time, high_freq = geometry.bounds

    return [
        Feature(name=DURATION, value=end_time - start_time),
        Feature(name=LOW_FREQ, value=low_freq),
        Feature(name=HIGH_FREQ, value=high_freq),
        Feature(name=BANDWIDTH, value=high_freq - low_freq),
    ]


def _compute_polygon_features(
    geometry: geometries.Polygon,
) -> List[Feature]:
    start_time, low_freq, end_time, high_freq = geometry.bounds

    return [
        Feature(name=DURATION, value=end_time - start_time),
        Feature(name=LOW_FREQ, value=low_freq),
        Feature(name=HIGH_FREQ, value=high_freq),
        Feature(name=BANDWIDTH, value=high_freq - low_freq),
    ]


def _compute_multi_point_features(
    geometry: geometries.MultiPoint,
) -> List[Feature]:
    start_time, low_freq, end_time, high_freq = geometry.bounds

    return [
        Feature(name=DURATION, value=end_time - start_time),
        Feature(name=LOW_FREQ, value=low_freq),
        Feature(name=HIGH_FREQ, value=high_freq),
        Feature(name=BANDWIDTH, value=high_freq - low_freq),
        Feature(name=NUM_SEGMENTS, value=len(geometry.coordinates)),
    ]


def _compute_multi_linestring_features(
    geometry: geometries.MultiLineString,
) -> List[Feature]:
    start_time, low_freq, end_time, high_freq = geometry.bounds

    return [
        Feature(name=DURATION, value=end_time - start_time),
        Feature(name=LOW_FREQ, value=low_freq),
        Feature(name=HIGH_FREQ, value=high_freq),
        Feature(name=BANDWIDTH, value=high_freq - low_freq),
        Feature(name=NUM_SEGMENTS, value=len(geometry.coordinates)),
    ]


def _compute_multi_polygon_features(
    geometry: geometries.MultiPolygon,
) -> List[Feature]:
    start_time, low_freq, end_time, high_freq = geometry.bounds

    return [
        Feature(name=DURATION, value=end_time - start_time),
        Feature(name=LOW_FREQ, value=low_freq),
        Feature(name=HIGH_FREQ, value=high_freq),
        Feature(name=BANDWIDTH, value=high_freq - low_freq),
        Feature(name=NUM_SEGMENTS, value=len(geometry.coordinates)),
    ]


_COMPUTE_FEATURES: Dict[
    geometries.GeometryType, Callable[[Any], List[Feature]]
] = {
    geometries.TimeStamp.geom_type(): _compute_time_stamp_features,
    geometries.TimeInterval.geom_type(): _compute_time_interval_features,
    geometries.BoundingBox.geom_type(): _compute_bounding_box_features,
    geometries.Point.geom_type(): _compute_point_features,
    geometries.LineString.geom_type(): _compute_line_string_features,
    geometries.Polygon.geom_type(): _compute_polygon_features,
    geometries.MultiPoint.geom_type(): _compute_multi_point_features,
    geometries.MultiLineString.geom_type(): _compute_multi_linestring_features,
    geometries.MultiPolygon.geom_type(): _compute_multi_polygon_features,
}


def compute_geometric_features(
    geometry: geometries.Geometry,
) -> List[Feature]:
    """Compute features from a geometry.

    Some basic acoustic features can be computed from a geometry. This function
    computes these features and returns them as a list of features.

    The following features are computed when possible:

    - ``duration``: The duration of the geometry.
    - ``low_freq``: The lowest frequency of the geometry.
    - ``high_freq``: The highest frequency of the geometry.
    - ``bandwidth``: The bandwidth of the geometry.
    - ``num_segments``: The number of segments in the geometry.

    Depending on the geometry type, some features may not be computed. For
    example, a ``TimeStamp`` geometry does not have a bandwidth.

    Parameters
    ----------
    geometry : geometries.Geometry
        The geometry to compute features from.

    Returns
    -------
    List[Feature]
        The computed features.

    Raises
    ------
    NotImplementedError
        If the geometry type is not supported.
    """
    try:
        return _COMPUTE_FEATURES[geometry.type](geometry)
    except KeyError as error:
        raise NotImplementedError(
            f"Geometry type {geometry.type} is not supported."
        ) from error
