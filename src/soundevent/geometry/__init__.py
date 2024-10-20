"""Geometry Module.

The geometry module in the `soundevent` package offers a set of essential
functions to handle sound event geometry objects effectively. It provides tools
to manage various aspects of sound event geometries, including operations like
overlap detection, geometry shifting, and transformations. These
functionalities are crucial in bioacoustic analysis, allowing users to
comprehend the geometric relationships between different sound events.

Understanding the spatial arrangement of sound events is pivotal in bioacoustic
research, enabling tasks such as matching sound event predictions with ground
truths for evaluation. The geometry module simplifies these tasks by providing
a clear and efficient interface for handling sound event geometries.
"""

from soundevent.geometry.conversion import geometry_to_shapely
from soundevent.geometry.features import compute_geometric_features
from soundevent.geometry.html import geometry_to_html
from soundevent.geometry.operations import (
    buffer_geometry,
    compute_bounds,
    get_geometry_point,
    group_sound_events,
    have_frequency_overlap,
    intervals_overlap,
    is_in_clip,
    rasterize,
)

__all__ = [
    "buffer_geometry",
    "compute_bounds",
    "compute_geometric_features",
    "geometry_to_html",
    "geometry_to_shapely",
    "get_geometry_point",
    "group_sound_events",
    "have_frequency_overlap",
    "have_frequency_overlap",
    "intervals_overlap",
    "is_in_clip",
    "rasterize",
]
