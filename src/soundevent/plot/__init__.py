"""Plotting utilities."""

from soundevent.plot.annotation import plot_annotation, plot_annotations
from soundevent.plot.common import create_axes
from soundevent.plot.geometries import plot_geometry
from soundevent.plot.prediction import plot_prediction, plot_predictions
from soundevent.plot.tags import TagColorMapper, add_tags_legend, plot_tag

__all__ = [
    "TagColorMapper",
    "add_tags_legend",
    "create_axes",
    "plot_annotation",
    "plot_annotations",
    "plot_geometry",
    "plot_prediction",
    "plot_predictions",
    "plot_tag",
]
