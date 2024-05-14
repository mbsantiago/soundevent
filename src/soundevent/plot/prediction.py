from typing import Iterable, Optional

from matplotlib.axes import Axes

from soundevent import data
from soundevent.geometry.operations import Positions, get_geometry_point
from soundevent.plot.common import create_axes
from soundevent.plot.geometries import plot_geometry
from soundevent.plot.tags import TagColorMapper, add_tags_legend, plot_tag

__all__ = [
    "plot_prediction",
    "plot_predictions",
]


def plot_prediction(
    prediction: data.SoundEventPrediction,
    ax: Optional[Axes] = None,
    position: Positions = "top-right",
    color_mapper: Optional[TagColorMapper] = None,
    time_offset: float = 0.001,
    freq_offset: float = 1000,
    max_alpha: float = 0.5,
    color: Optional[str] = None,
    **kwargs,
) -> Axes:
    """Plot an annotation."""
    geometry = prediction.sound_event.geometry

    if geometry is None:
        raise ValueError("Annotation does not have a geometry.")

    if ax is None:
        ax = create_axes(**kwargs)

    if color_mapper is None:
        color_mapper = TagColorMapper()

    ax = plot_geometry(
        geometry,
        ax=ax,
        color=color,
        alpha=prediction.score * max_alpha,
        **kwargs,
    )

    x, y = get_geometry_point(geometry, position=position)

    for index, tag in enumerate(prediction.tags):
        color = color_mapper.get_color(tag.tag)
        ax = plot_tag(
            time=x + time_offset,
            frequency=y - index * freq_offset,
            color=color,
            ax=ax,
            alpha=prediction.score,
            **kwargs,
        )

    return ax


def plot_predictions(
    predictions: Iterable[data.SoundEventPrediction],
    ax: Optional[Axes] = None,
    position: Positions = "top-right",
    color_mapper: Optional[TagColorMapper] = None,
    time_offset: float = 0.001,
    freq_offset: float = 1000,
    legend: bool = True,
    max_alpha: float = 0.5,
    color: Optional[str] = None,
    **kwargs,
):
    """Plot an prediction."""
    if ax is None:
        ax = create_axes(**kwargs)

    if color_mapper is None:
        color_mapper = TagColorMapper()

    for prediction in predictions:
        ax = plot_prediction(
            prediction,
            ax=ax,
            position=position,
            color_mapper=color_mapper,
            time_offset=time_offset,
            freq_offset=freq_offset,
            max_alpha=max_alpha,
            color=color,
            **kwargs,
        )

    if legend:
        ax = add_tags_legend(ax, color_mapper)

    return ax
