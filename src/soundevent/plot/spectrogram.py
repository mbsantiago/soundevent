"""Functions for plotting spectrograms."""

from typing import Optional

import matplotlib.pyplot as plt
import xarray as xr
from matplotlib.axes import Axes

from soundevent.plot.common import create_axes

__all__ = ["plot_spectrogram"]


def plot_spectrogram(
    spectrogram: xr.DataArray,
    channel: int = 0,
    ax: Optional[Axes] = None,
    vmax: Optional[float] = None,
    vmin: Optional[float] = None,
    cmap: Optional[str] = "magma",
    colorbar: bool = False,
    **kwargs,
) -> Axes:
    """Plot a spectrogram.

    Parameters
    ----------
    spectrogram
        The spectrogram to plot.
    channel
        The channel to plot.
    ax
        The axes on which to plot. If None, a new figure is
        created.
    vmax
        The maximum value of the amplitude scale. If None, the
        maximum value of the spectrogram is used.
    vmin
        The minimum value of the amplitude scale. If None, the
        minimum value of the spectrogram is used.
    cmap
        Colormap to use to map amplitude values to colors.
    colorbar
        Whether to add a colorbar to the plot.
    **kwargs
        Additional arguments passed to `create_axes`.

    Returns
    -------
    ax
        The axes on which the spectrogram was plotted.
    """
    if ax is None:
        ax = create_axes(**kwargs)

    mapping = ax.pcolormesh(
        spectrogram.time,
        spectrogram.frequency,
        spectrogram.sel(channel=channel),
        shading="auto",
        vmax=vmax,
        vmin=vmin,
        cmap=cmap,
    )
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    ax.set_title(f"Channel {channel}")

    if colorbar:
        plt.colorbar(mapping, ax=ax)

    return ax
