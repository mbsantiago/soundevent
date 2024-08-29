"""Functions for plotting tags."""

from itertools import cycle
from typing import Dict, Optional

import numpy as np
from matplotlib import colormaps
from matplotlib.axes import Axes

from soundevent import data
from soundevent.plot.common import create_axes

__all__ = [
    "plot_tag",
    "add_tags_legend",
    "TagColorMapper",
]


class TagColorMapper:
    """Maps tags to colors."""

    def __init__(
        self,
        cmap: str = "tab20",
        num_colors: int = 20,
    ):
        """Initialize color mapper."""
        self._tags: Dict[data.Tag, str] = {}

        colormap = colormaps.get_cmap(cmap)
        self._colors = cycle(
            [colormap(x) for x in np.linspace(0, 1, num_colors)]
        )

    def get_color(self, tag: data.Tag) -> str:
        """Get color for tag."""
        if tag not in self._tags:
            self._tags[tag] = next(self._colors)  # type: ignore

        return self._tags[tag]


def plot_tag(
    time: float,
    frequency: float,
    color: str,
    ax: Optional[Axes] = None,
    size: int = 10,
    **kwargs,
) -> Axes:
    """Plot a tag."""
    if ax is None:
        ax = create_axes(**kwargs)

    ax.scatter(
        time,
        frequency,
        marker="o",
        color=color,
        s=size,
    )

    return ax


def add_tags_legend(
    ax: Axes,
    color_mapper: TagColorMapper,
) -> Axes:
    """Add a legend for tags."""
    handles = []
    labels = []

    for tag in color_mapper._tags:
        color = color_mapper.get_color(tag)
        handles.append(ax.scatter([], [], color=color))
        labels.append(f"{tag.term.label}: {tag.value}")

    ax.legend(handles, labels, loc="upper right")

    return ax
