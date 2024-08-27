"""Functions for plotting sound event geometries."""

from typing import Dict, Optional, Protocol, Tuple

import shapely
from matplotlib.axes import Axes
from shapely.plotting import plot_line, plot_points, plot_polygon

from soundevent import data
from soundevent.geometry import geometry_to_shapely
from soundevent.plot.common import create_axes

__all__ = [
    "plot_geometry",
]


class GeometryPlotter(Protocol):
    def __call__(
        self,
        geometry: data.Geometry,
        ax: Axes,
        **kwargs,
    ) -> Axes: ...


def plot_geometry(
    geometry: data.Geometry,
    ax: Optional[Axes] = None,
    figsize: Optional[Tuple[float, float]] = None,
    **kwargs,
) -> Axes:
    """Plot a geometry in the given ax."""
    if ax is None:
        ax = create_axes(figsize=figsize)

    geometry_type = geometry.type

    plotter = _GEOMETRY_PLOTTERS.get(geometry_type, None)

    if plotter is None:
        raise NotImplementedError(
            f"Plotting geometry of type {geometry_type} is not implemented."
        )

    ax = plotter(geometry, ax=ax, **kwargs)

    return ax


def _plot_timestamp_geometry(
    geometry: data.Geometry,
    ax: Axes,
    **kwargs,
) -> Axes:
    if not isinstance(geometry, data.TimeStamp):
        raise ValueError(
            f"Expected geometry of type {data.TimeStamp}, "
            f"got {type(geometry)}."
        )

    time = geometry.coordinates
    ax.axvline(time, **kwargs)  # type: ignore
    return ax


def _plot_timeinterval_geometry(
    geometry: data.Geometry,
    ax: Axes,
    alpha: float = 1,
    **kwargs,
) -> Axes:
    if not isinstance(geometry, data.TimeInterval):
        raise ValueError(
            f"Expected geometry of type {data.TimeInterval}, "
            f"got {type(geometry)}."
        )

    start_time, end_time = geometry.coordinates
    ax.axvline(start_time, alpha=alpha, **kwargs)  # type: ignore
    ax.axvspan(start_time, end_time, alpha=alpha * 0.5, **kwargs)  # type: ignore
    ax.axvline(end_time, alpha=alpha, **kwargs)  # type: ignore
    return ax


def _plot_point_geometry(
    geometry: data.Geometry,
    ax: Axes,
    **kwargs,
) -> Axes:
    if not isinstance(geometry, (data.Point, data.MultiPoint)):
        raise ValueError(
            "Expected geometry of type "
            f"{data.Point} or {data.MultiPoint}, "
            f"got {type(geometry)}."
        )

    shapely_geometry = geometry_to_shapely(geometry)
    plot_points(shapely_geometry, ax=ax, **kwargs)
    return ax


def _plot_line_string_geometry(
    geometry: data.Geometry,
    ax: Axes,
    **kwargs,
) -> Axes:
    if not isinstance(geometry, (data.LineString, data.MultiLineString)):
        raise ValueError(
            "Expected geometry of type "
            f"{data.LineString} or {data.MultiLineString}, "
            f"got {type(geometry)}."
        )

    shapely_geometry = geometry_to_shapely(geometry)
    if not isinstance(
        shapely_geometry,
        (shapely.LineString, shapely.MultiLineString, shapely.LinearRing),
    ):
        raise ValueError(
            "Expected geometry of type "
            f"{shapely.LineString}, {shapely.MultiLineString} or {shapely.LinearRing}, "
            f"got {type(geometry)}."
        )
    plot_line(shapely_geometry, ax=ax, **kwargs)
    return ax


def _plot_polygon_geometry(
    geometry: data.Geometry,
    ax: Axes,
    **kwargs,
) -> Axes:
    if not isinstance(
        geometry, (data.Polygon, data.MultiPolygon, data.BoundingBox)
    ):
        raise ValueError(
            "Expected geometry of type "
            f"{data.Polygon}, {data.MultiPolygon} or {data.BoundingBox}, "
            f"got {type(geometry)}."
        )

    shapely_geometry = geometry_to_shapely(geometry)

    if not isinstance(
        shapely_geometry,
        (shapely.Polygon, shapely.MultiPolygon),
    ):
        raise ValueError(
            "Expected geometry of type "
            f"{shapely.Polygon}, {shapely.MultiPolygon} or {shapely.LinearRing}, "
            f"got {type(geometry)}."
        )

    plot_polygon(shapely_geometry, ax=ax, **kwargs)
    return ax


_GEOMETRY_PLOTTERS: Dict[data.GeometryType, GeometryPlotter] = {
    data.BoundingBox.geom_type(): _plot_polygon_geometry,
    data.TimeStamp.geom_type(): _plot_timestamp_geometry,
    data.TimeInterval.geom_type(): _plot_timeinterval_geometry,
    data.Point.geom_type(): _plot_point_geometry,
    data.LineString.geom_type(): _plot_line_string_geometry,
    data.Polygon.geom_type(): _plot_polygon_geometry,
    data.MultiPolygon.geom_type(): _plot_polygon_geometry,
    data.MultiLineString.geom_type(): _plot_line_string_geometry,
}
