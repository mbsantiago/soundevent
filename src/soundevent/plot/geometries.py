"""Functions for plotting sound event geometries."""
import sys
from typing import Dict, Optional

from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from soundevent import data
from soundevent.plot.common import create_axes

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


__all__ = [
    "plot_geometry",
]


class GeometryPlotter(Protocol):
    def __call__(
        self,
        geometry: data.Geometry,
        ax: Axes,
        **kwargs,
    ) -> Axes:
        ...


def plot_geometry(
    geometry: data.Geometry,
    ax: Optional[Axes] = None,
    **kwargs,
) -> Axes:
    if ax is None:
        ax = create_axes(**kwargs)

    geometry_type = geometry.type

    plotter = _GEOMETRY_PLOTTERS.get(geometry_type, None)

    if plotter is None:
        raise NotImplementedError(
            f"Plotting geometry of type {geometry_type} is not implemented."
        )

    ax = plotter(geometry, ax=ax, **kwargs)

    return ax


def _plot_bounding_box_geometry(
    geometry: data.Geometry,
    ax: Axes,
    **kwargs,
) -> Axes:
    if not isinstance(geometry, data.BoundingBox):
        raise ValueError(
            f"Expected geometry of type {data.BoundingBox}, "
            f"got {type(geometry)}."
        )

    start_time, low_freq, end_time, high_freq = geometry.coordinates

    rect = Rectangle(
        (start_time, low_freq),
        end_time - start_time,
        high_freq - low_freq,
        **kwargs,
    )

    ax.add_patch(rect)

    return ax


_GEOMETRY_PLOTTERS: Dict[data.GeometryType, GeometryPlotter] = {
    data.BoundingBox.geom_type(): _plot_bounding_box_geometry,
}
