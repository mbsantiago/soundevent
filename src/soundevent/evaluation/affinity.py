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


def compute_affinity(
    geometry1: data.Geometry,
    geometry2: data.Geometry,
    time_buffer: float = 0.01,
    freq_buffer: float = 100,
) -> float:
    r"""Compute the geometric affinity between two geometries.

    This function calculates the geometric similarity between two geometries,
    which is a measure of how much they overlap. The affinity is computed as
    the Intersection over Union (IoU).

    **Intersection over Union (IoU)**

    IoU is a standard metric for comparing the similarity between two shapes.
    It is calculated as the ratio of the area of the overlap between the two
    geometries to the area of their combined shape.

    .. math::

        \text{IoU} = \frac{\text{Area of Overlap}}{\text{Area of Union}}

    An IoU of 1 means the geometries are identical, while an IoU of 0 means
    they do not overlap at all. This is particularly useful in bioacoustics
    for comparing annotations or predictions of sound events in a
    time-frequency representation (spectrogram).

    To account for small variations in annotations, a buffer can be added to
    each geometry before computing the IoU. This is controlled by the
    `time_buffer` and `freq_buffer` parameters.

    Parameters
    ----------
    geometry1
        The first geometry to be compared.
    geometry2
        The second geometry to be compared.
    time_buffer
        Time buffer in seconds added to each geometry. Default is 0.01.
    freq_buffer
        Frequency buffer in Hertz added to each geometry. Default is 100.

    Returns
    -------
    affinity : float
        The Intersection over Union (IoU) score, a value between 0 and 1
        indicating the degree of overlap.

    Notes
    -----
    - If either input geometry is of a time-based type, a specialized
    time-based affinity calculation is performed.

    Examples
    --------
    >>> geometry1 = data.BoundingBox(coordinates=[0.4, 2000, 0.6, 8000])
    >>> geometry2 = data.BoundingBox(coordinates=[0.5, 5000, 0.7, 6000])
    >>> affinity = compute_affinity(
    ...     geometry1,
    ...     geometry2,
    ...     time_buffer=0.02,
    ...     freq_buffer=150,
    ... )
    >>> print(round(affinity, 3))
    0.111
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
    return buffer_geometry(
        geometry,
        time_buffer=time_buffer,
        freq_buffer=freq_buffer,
    )
