"""Common utilities for plotting."""

from typing import Optional, Tuple

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

__all__ = ["create_axes"]


def create_axes(
    figsize: Optional[Tuple[float, float]] = None,
) -> Axes:
    """Create a new figure and axes.

    Parameters
    ----------
    figsize
        The size of the figure. If None, use the default size.

    Returns
    -------
    ax
        The axes.
    """
    _, ax = plt.subplots(figsize=figsize)  # type: ignore
    return ax  # type: ignore
