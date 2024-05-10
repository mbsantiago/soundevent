"""Measures of affinity between sound events geometries."""

from soundevent import data
from soundevent.geometry import (
    buffer_geometry,
    compute_bounds,
    geometry_to_shapely,
)

__all__ = [
    "compute_affinity",
]


TIME_GEOMETRY_TYPES = {
    data.TimeStamp.geom_type(),
    data.TimeInterval.geom_type(),
}


BUFFER_GEOMETRY_TYPES = {
    data.TimeStamp.geom_type(),
    data.Point.geom_type(),
    data.MultiPoint.geom_type(),
    data.LineString.geom_type(),
    data.MultiLineString.geom_type(),
}


def compute_affinity(
    geometry1: data.Geometry,
    geometry2: data.Geometry,
    time_buffer: float = 0.01,
    freq_buffer: float = 100,
) -> float:
    """Compute the geometric affinity between two geometries.

    This function calculates the geometric similarity between two input
    geometries in the context of time-frequency space. The geometric affinity
    metric indicates how similar the two geometries are, with a value ranging
    from 0 (no similarity) to 1 (perfect similarity).

    Parameters
    ----------
    geometry1
        The first geometry to be compared.
    geometry2
        The second geometry to be compared.
    time_buffer
        Time buffer for geometric preparation. Default is 0.01.
    freq_buffer
        Frequency buffer for geometric preparation. Default is 100.

    Returns
    -------
    affinity: float
        A metric indicating the geometric similarity between the input
        geometries.

        - 0: The geometries have no overlap
        - 1: The geometries perfectly overlap.

        The value is a ratio of the intersection area to the union area of the
        two geometries.

    Notes
    -----
    - 0 or 1-dimensional geometries are buffered to 2-dimensional using
    the specified time and frequency buffers.
    - If either input geometry is of a time-based type, a specialized
    time-based affinity calculation is performed.
    - The function utilizes the Shapely library for geometric operations.

    Examples
    --------
    >>> geometry1 = data.Geometry(...)  # Define the first geometry
    >>> geometry2 = data.Geometry(...)  # Define the second geometry
    >>> affinity = compute_affinity(
    ...     geometry1,
    ...     geometry2,
    ...     time_buffer=0.02,
    ...     freq_buffer=150,
    ... )
    >>> affinity
    0.75
    """
    geometry1 = _prepare_geometry(geometry1, time_buffer, freq_buffer)
    geometry2 = _prepare_geometry(geometry2, time_buffer, freq_buffer)

    if (
        geometry1.type in TIME_GEOMETRY_TYPES
        or geometry2.type in TIME_GEOMETRY_TYPES
    ):
        return compute_affinity_in_time(geometry1, geometry2)

    shp1 = geometry_to_shapely(geometry1)
    shp2 = geometry_to_shapely(geometry2)

    intersection = shp1.intersection(shp2).area
    union = shp1.area + shp2.area - intersection

    if union == 0:
        return 0

    return intersection / union


def compute_affinity_in_time(
    geometry1: data.Geometry,
    geometry2: data.Geometry,
) -> float:
    """Compute the temporal affinity between two geometries."""
    start_time1, _, end_time1, _ = compute_bounds(geometry1)
    start_time2, _, end_time2, _ = compute_bounds(geometry2)

    intersection = max(
        0, min(end_time1, end_time2) - max(start_time1, start_time2)
    )
    union = (
        (end_time1 - start_time1) + (end_time2 - start_time2) - intersection
    )

    if union == 0:
        return 0

    return intersection / union


def _prepare_geometry(
    geometry: data.Geometry,
    time_buffer: float = 0.01,
    freq_buffer: float = 100,
) -> data.Geometry:
    if geometry.type in BUFFER_GEOMETRY_TYPES:
        return buffer_geometry(
            geometry,
            time_buffer=time_buffer,
            freq_buffer=freq_buffer,
        )

    return geometry
