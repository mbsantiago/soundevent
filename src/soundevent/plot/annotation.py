"""Functions for plotting annotations."""

from typing import Callable, Dict, Optional, Tuple

from matplotlib.axes import Axes

from soundevent import data
from soundevent.plot.common import create_axes
from soundevent.plot.geometries import plot_geometry
from soundevent.plot.tags import TagColorMapper, plot_tag

__all__ = ["plot_annotation"]


def plot_annotation(
    annotation: data.SoundEventAnnotation,
    ax: Optional[Axes] = None,
    color_mapper: Optional[TagColorMapper] = None,
    time_offset: float = 0.001,
    freq_offset: float = 1000,
    **kwargs,
) -> Axes:
    """Plot an annotation."""

    geometry = annotation.sound_event.geometry

    if geometry is None:
        raise ValueError("Annotation does not have a geometry.")

    if ax is None:
        ax = create_axes(**kwargs)

    if color_mapper is None:
        color_mapper = TagColorMapper()

    ax = plot_geometry(geometry, ax=ax, **kwargs)

    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    x, y = get_tags_position(geometry, (xmin, xmax, ymin, ymax))

    for index, tag in enumerate(annotation.tags):
        color = color_mapper.get_color(tag)
        ax = plot_tag(
            time=x + time_offset,
            frequency=y - index * freq_offset,
            color=color,
            ax=ax,
            **kwargs,
        )

    return ax


def get_tags_position(
    geometry: data.Geometry,
    bounds: Tuple[float, float, float, float],
) -> Tuple[float, float]:
    """Compute the best position for tag plotting.

    Parameters
    ----------
    geometry : data.Geometry
        Geometry to plot tags next to.

    Returns
    -------
    float
        Time position for tag plotting in seconds.
    float
        Frequency position for tag plotting in Hertz.
    """

    func = _TAG_POSITION_FUNCTIONS.get(geometry.type, None)

    if func is None:
        raise NotImplementedError(
            f"Plotting tags for geometry of type {geometry.type} "
            "is not implemented."
        )

    return func(geometry, bounds)


def _get_tags_position_bounding_box(
    geometry: data.Geometry,
    bounds: Tuple[float, float, float, float],
) -> Tuple[float, float]:
    """Compute the best position for tag plotting for bounding box geometries.

    Parameters
    ----------
    geometry : data.BoundingBox
        Bounding box geometry to plot tags next to.
    bounds : Tuple[float, float, float, float]
        Bounds of the plot.

    Returns
    -------
    float
        Time position for tag plotting in seconds.
    float
        Frequency position for tag plotting in Hertz.
    """
    if not isinstance(geometry, data.BoundingBox):
        raise ValueError(
            f"Geometry must be of type {data.BoundingBox}, "
            f"but is of type {type(geometry)}."
        )

    start_time, low_freq, end_time, high_freq = geometry.coordinates
    _, x_max, _, y_max = bounds
    x = end_time if end_time < x_max else start_time
    y = high_freq if high_freq < y_max else low_freq
    return x, y


_TAG_POSITION_FUNCTIONS: Dict[
    data.GeometryType,
    Callable[
        [data.Geometry, Tuple[float, float, float, float]], Tuple[float, float]
    ],
] = {
    data.BoundingBox.geom_type(): _get_tags_position_bounding_box,
}
