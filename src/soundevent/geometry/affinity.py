"""Measures of affinity between geometries."""

from typing import Callable

from soundevent import data
from soundevent.geometry.conversion import geometry_to_shapely
from soundevent.geometry.operations import (
    compute_bbox_area,
    compute_bounds,
    compute_interval_overlap,
    compute_interval_width,
    get_point_in_frequency,
    get_point_in_time,
)

__all__ = [
    "AffinityFn",
    "compute_bbox_iou",
    "compute_frequency_iou",
    "compute_geometric_iou",
    "compute_spectral_closeness",
    "compute_temporal_closeness",
    "compute_temporal_iou",
]

AffinityFn = Callable[[data.Geometry, data.Geometry], float]
"""Type for functions that compute similarity scores between geometries."""


def compute_temporal_closeness(
    geometry1: data.Geometry,
    geometry2: data.Geometry,
    ratio: float = 0,
    max_distance: float = 0.1,
) -> float:
    """Compute the proximity of two geometries in time.

    Parameters
    ----------
    geometry1 : data.Geometry
        The first geometry object.
    geometry2 : data.Geometry
        The second geometry object.
    ratio : float, optional
        The relative time point to compare (0.0 to 1.0).
        Defaults to 0 (compares start times). Use 0.5 to compare
        temporal centers.
    max_distance : float, optional
        The maximum time distance (in seconds) allowed for a non-zero score.
        Defaults to 0.1.

    Returns
    -------
    float
        A closeness score between 0.0 and 1.0.
        * **1.0**: The time points are identical.
        * **0.0**: The distance is greater than or equal to ``max_distance``.
        * **0.0 < x < 1.0**: Linearly decays as distance increases.

    Notes
    -----
    This function measures the absolute distance between the specific time
    points derived from the ``ratio``. The score decays linearly from 1 to 0
    as the distance grows from 0 to ``max_distance``.
    """
    if max_distance <= 0:
        raise ValueError("max_distance must be greater than 0")

    point1 = get_point_in_time(geometry1, ratio)
    point2 = get_point_in_time(geometry2, ratio)

    distance = abs(point1 - point2)
    if distance > max_distance:
        return 0

    return 1 - distance / max_distance


def compute_spectral_closeness(
    geometry1: data.Geometry,
    geometry2: data.Geometry,
    ratio: float = 0,
    max_distance: float = 1_000,
) -> float:
    """Compute the proximity of two geometries in frequency.

    Parameters
    ----------
    geometry1 : data.Geometry
        The first geometry object.
    geometry2 : data.Geometry
        The second geometry object.
    ratio : float, optional
        The relative frequency point to compare (0.0 to 1.0).
        Defaults to 0 (compares lowest frequencies). Use 0.5 to compare
        center frequencies.
    max_distance : float, optional
        The maximum frequency distance (in Hertz) allowed for a non-zero
        score. Defaults to 1000 Hz.

    Returns
    -------
    float
        A closeness score between 0.0 and 1.0.
        * **1.0**: The frequency points are identical.
        * **0.0**: The distance is greater than or equal to ``max_distance``.
        * **0.0 < x < 1.0**: Linearly decays as distance increases.

    Notes
    -----
    This function measures the absolute distance between the specific frequency
    points derived from the ``ratio``. The score decays linearly from 1 to 0 as
    the distance grows from 0 to ``max_distance``.
    """
    if max_distance <= 0:
        raise ValueError("max_distance must be greater than 0")

    point1 = get_point_in_frequency(geometry1, ratio)
    point2 = get_point_in_frequency(geometry2, ratio)

    distance = abs(point1 - point2)
    if distance > max_distance:
        return 0

    return 1 - distance / max_distance


def compute_temporal_iou(
    geometry1: data.Geometry,
    geometry2: data.Geometry,
) -> float:
    """Compute the IoU of the temporal extents of two geometries.

    Parameters
    ----------
    geometry1 : data.Geometry
        The first geometry object.
    geometry2 : data.Geometry
        The second geometry object.

    Returns
    -------
    float
        The IoU score, a value between 0.0 and 1.0.

    Notes
    -----
    This function projects the geometries onto the time axis and computes
    the Intersection over Union of the resulting time intervals.

    This metric ignores the frequency content completely. Two events
    occurring at the exact same time will have a score of 1.0, even if
    one is low frequency and the other is high frequency.
    """
    start_time1, _, end_time1, _ = compute_bounds(geometry1)
    start_time2, _, end_time2, _ = compute_bounds(geometry2)
    interval1 = (start_time1, end_time1)
    interval2 = (start_time2, end_time2)

    intersection = compute_interval_overlap(interval1, interval2)

    if intersection == 0:
        return 0

    area1 = compute_interval_width(interval1)
    area2 = compute_interval_width(interval2)
    union = area1 + area2 - intersection
    return intersection / union


def compute_frequency_iou(
    geometry1: data.Geometry,
    geometry2: data.Geometry,
) -> float:
    """Compute the IoU of the frequency extents of two geometries.

    Parameters
    ----------
    geometry1 : data.Geometry
        The first geometry object.
    geometry2 : data.Geometry
        The second geometry object.

    Returns
    -------
    float
        The IoU score, a value between 0.0 and 1.0.

    Notes
    -----
    This function projects the geometries onto the frequency axis and
    computes the Intersection over Union of the resulting frequency
    intervals (bandwidths).

    This metric ignores the time component completely. Two events with the
    same pitch range will have a score of 1.0, even if they occur at
    completely different times in the recording.
    """
    _, low_freq1, _, high_freq1 = compute_bounds(geometry1)
    _, low_freq2, _, high_freq2 = compute_bounds(geometry2)
    interval1 = (low_freq1, high_freq1)
    interval2 = (low_freq2, high_freq2)

    intersection = compute_interval_overlap(interval1, interval2)

    if intersection == 0:
        return 0

    area1 = compute_interval_width(interval1)
    area2 = compute_interval_width(interval2)
    union = area1 + area2 - intersection
    return intersection / union


def compute_bbox_iou(
    geometry1: data.Geometry,
    geometry2: data.Geometry,
) -> float:
    """Compute the IoU of the bounding boxes of two geometries.

    Parameters
    ----------
    geometry1 : data.Geometry
        The first geometry object.
    geometry2 : data.Geometry
        The second geometry object.

    Returns
    -------
    float
        The IoU score, a value between 0.0 and 1.0.

    Notes
    -----
    This function compares the *bounding boxes* of the geometries, not the
    exact shapes. For example, if you compare two diagonal lines that cross
    each other, their exact overlap might be small, but their bounding boxes
    might overlap significantly. This makes this function a fast, "coarse"
    filter for similarity. If you want to compute the true geometric IoU, use
    the [`compute_geometric_iou`][soundevent.geometry.compute_geometric_iou]
    function.

    Unlike [`compute_bbox_area`][soundevent.geometry.compute_bbox_area], the
    IoU is a ratio and therefore scale-invariant. Stretching the frequency or
    temporal axis does not change the ratio of overlap. Hence, no scaling is
    required before computing the IoU.
    """
    bbox1 = compute_bounds(geometry1)
    bbox2 = compute_bounds(geometry2)

    time_intersection = compute_interval_overlap(
        (bbox1[0], bbox1[2]),
        (bbox2[0], bbox2[2]),
    )
    freq_intersection = compute_interval_overlap(
        (bbox1[1], bbox1[3]),
        (bbox2[1], bbox2[3]),
    )
    intersection = time_intersection * freq_intersection

    if intersection == 0:
        return 0

    union = compute_bbox_area(bbox1) + compute_bbox_area(bbox2) - intersection
    return intersection / union


def compute_geometric_iou(
    geometry1: data.Geometry,
    geometry2: data.Geometry,
) -> float:
    r"""Compute the IoU of two geometries.

    This function calculates the geometric similarity between two geometries,
    which is a measure of how much they overlap. The affinity is computed as
    the Intersection over Union (IoU).

    IoU is a standard metric for comparing the similarity between two shapes.
    It is calculated as the ratio of the area of the overlap between the two
    geometries to the area of their combined shape.

    $$
        \text{IoU} = \frac{\text{Area of Overlap}}{\text{Area of Union}}
    $$

    An IoU of 1 means the geometries are identical, while an IoU of 0 means
    they do not overlap at all.

    Parameters
    ----------
    geometry1
        The first geometry to be compared.
    geometry2
        The second geometry to be compared.

    Returns
    -------
    affinity : float
        The Intersection over Union (IoU) score, a value between 0 and 1
        indicating the degree of overlap.

    Examples
    --------
    >>> from soundevent.geometry import compute_geometric_iou
    >>> geometry1 = data.BoundingBox(coordinates=[0.4, 2000, 0.6, 8000])
    >>> geometry2 = data.BoundingBox(coordinates=[0.5, 5000, 0.7, 6000])
    >>> affinity = compute_geometric_iou(geometry1, geometry2)
    >>> print(round(affinity, 3))
    0.077
    """
    shp1 = geometry_to_shapely(geometry1)
    shp2 = geometry_to_shapely(geometry2)

    intersection = shp1.intersection(shp2).area
    union = shp1.area + shp2.area - intersection

    if union == 0:
        return 0

    return intersection / union
