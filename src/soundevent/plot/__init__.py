"""Plotting utilities."""
from soundevent.plot.annotation import plot_annotation
from soundevent.plot.geometries import plot_geometry
from soundevent.plot.spectrogram import plot_spectrogram
from soundevent.plot.tags import TagColorMapper, add_tags_legend, plot_tag

__all__ = [
    "TagColorMapper",
    "plot_annotation",
    "plot_geometry",
    "plot_spectrogram",
    "plot_tag",
    "add_tags_legend",
]
