from typing import Literal, Tuple

import shapely

from soundevent.data import Geometry
from soundevent.geometry.conversion import geometry_to_shapely
from soundevent.geometry.operations import compute_bounds

__all__ = [
    "get_geometry_point",
]


def get_geometry_point(
    geometry: Geometry,
    point_type: Literal[
        "bottom-left",
        "bottom-right",
        "top-left",
        "top-right",
        "center-left",
        "center-right",
        "top-center",
        "bottom-center",
        "center",
        "centroid",
        "point_on_surface",
    ] = "bottom-left",
) -> Tuple[float, float]:
    """
    Calculate the coordinates of a specific point within a geometry.

    Parameters
    ----------
    geometry
        The geometry object for which to calculate the point coordinates.
    point_type
        The specific point within the geometry to calculate coordinates for.
        Defaults to 'bottom-left'.

    Returns
    -------
    Tuple[float, float]
        The coordinates of the specified point within the geometry.

    Raises
    ------
    ValueError
        If an invalid point is specified.

    Notes
    -----
    The following points are supported:
    - 'bottom-left': The point defined by the start time and lowest frequency
        of the geometry.
    - 'bottom-right': The point defined by the end time and lowest frequency
        of the geometry.
    - 'top-left': The point defined by the start time and highest frequency
        of the geometry.
    - 'top-right': The point defined by the end time and highest frequency
        of the geometry.
    - 'center-left': The point defined by the middle time and lowest frequency
        of the geometry.
    - 'center-right': The point defined by the middle time and highest frequency
        of the geometry.
    - 'top-center': The point defined by the end time and middle frequency
        of the geometry.
    - 'bottom-center': The point defined by the start time and middle frequency
        of the geometry.
    - 'center': The point defined by the middle time and middle frequency
        of the geometry.
    - 'centroid': The centroid of the geometry. Computed using the shapely
        library.
    - 'point_on_surface': A point on the surface of the geometry. Computed
        using the shapely library.

    For all points except 'centroid' and 'point_on_surface', the time and
    frequency values are calculated by first computing the bounds of the
    geometry and then determining the appropriate values based on the
    specified point type.
    """
    if point_type not in [
        "bottom-left",
        "bottom-right",
        "top-left",
        "top-right",
        "center-left",
        "center-right",
        "top-center",
        "bottom-center",
        "center",
        "centroid",
        "point_on_surface",
    ]:
        raise ValueError(f"Invalid point type: {point_type}")

    if point_type == "centroid":
        shp_geom = geometry_to_shapely(geometry)
        return shp_geom.centroid.coords[0]

    if point_type == "point_on_surface":
        shp_geom = geometry_to_shapely(geometry)
        return shapely.point_on_surface(shp_geom).coords[0]

    start_time, low_freq, end_time, high_freq = compute_bounds(geometry)

    if point_type == "center":
        return (start_time + end_time) / 2, (low_freq + high_freq) / 2

    x, y = point_type.split("-")

    time_pos = {
        "left": start_time,
        "center": (start_time + end_time) / 2,
        "right": end_time,
    }[x]

    freq_pos = {
        "bottom": low_freq,
        "center": (low_freq + high_freq) / 2,
        "right": high_freq,
    }[y]

    return time_pos, freq_pos
