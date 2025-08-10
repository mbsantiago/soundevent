"""Functions for plotting annotations."""

from typing import Iterable, Optional

from matplotlib.axes import Axes

from soundevent import data
from soundevent.geometry.operations import Positions, get_geometry_point
from soundevent.plot.common import create_axes
from soundevent.plot.geometries import plot_geometry
from soundevent.plot.tags import TagColorMapper, add_tags_legend, plot_tag

__all__ = [
    "plot_annotation",
    "plot_annotations",
]


def plot_annotation(
    annotation: data.SoundEventAnnotation,
    ax: Optional[Axes] = None,
    position: Positions = "top-right",
    color_mapper: Optional[TagColorMapper] = None,
    time_offset: float = 0.001,
    freq_offset: float = 1000,
    color: Optional[str] = None,
    **kwargs,
) -> Axes:
    """Plot a sound event annotation on a spectrogram.

    This function plots the geometry of the sound event and its associated
    tags.

    Parameters
    ----------
    annotation
        The sound event annotation to plot.
    ax
        The matplotlib axes to plot on. If None, a new one is created.
    position
        The position of the tags relative to the geometry.
    color_mapper
        A `TagColorMapper` instance to map tags to colors. If None, a new
        one is created.
    time_offset
        The time offset for positioning the tags.
    freq_offset
        The frequency offset for positioning the tags.
    color
        The color of the geometry. If None, the color is determined by the
        color mapper.
    **kwargs
        Additional keyword arguments passed to `create_axes` and
        `plot_geometry`.

    Returns
    -------
    Axes
        The matplotlib axes with the annotation plotted.
    """
    geometry = annotation.sound_event.geometry

    if geometry is None:
        raise ValueError("Annotation does not have a geometry.")

    if ax is None:
        ax = create_axes(**kwargs)

    if color_mapper is None:
        color_mapper = TagColorMapper()

    ax = plot_geometry(geometry, ax=ax, color=color, **kwargs)

    x, y = get_geometry_point(geometry, position=position)

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


def plot_annotations(
    annotations: Iterable[data.SoundEventAnnotation],
    ax: Optional[Axes] = None,
    position: Positions = "top-right",
    color_mapper: Optional[TagColorMapper] = None,
    time_offset: float = 0.001,
    freq_offset: float = 1000,
    legend: bool = True,
    color: Optional[str] = None,
    **kwargs,
):
    """Plot a collection of sound event annotations on a spectrogram.

    This function iterates through a collection of sound event annotations
    and plots each one on the provided matplotlib axes.

    Parameters
    ----------
    annotations
        An iterable of `SoundEventAnnotation` objects to plot.
    ax
        The matplotlib axes to plot on. If None, a new one is created.
    position
        The position of the tags relative to the geometry.
    color_mapper
        A `TagColorMapper` instance to map tags to colors. If None, a new
        one is created.
    time_offset
        The time offset for positioning the tags.
    freq_offset
        The frequency offset for positioning the tags.
    legend
        Whether to add a legend for the tags.
    color
        The color of the geometries. If None, the color is determined by
        the color mapper.
    **kwargs
        Additional keyword arguments passed to `plot_annotation`.

    Returns
    -------
    Axes
        The matplotlib axes with the annotations plotted.
    """
    if ax is None:
        ax = create_axes(**kwargs)

    if color_mapper is None:
        color_mapper = TagColorMapper()

    for annotation in annotations:
        ax = plot_annotation(
            annotation,
            ax=ax,
            position=position,
            color_mapper=color_mapper,
            time_offset=time_offset,
            freq_offset=freq_offset,
            color=color,
            **kwargs,
        )

    if legend:
        ax = add_tags_legend(ax, color_mapper)

    return ax
