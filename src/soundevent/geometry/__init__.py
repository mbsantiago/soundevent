"""Tools for geometric operations on Time-Frequency planes.

This module provides functions to manipulate, compare, and analyse sound event
geometries (regions of interest defined by time and frequency coordinates).

Key Tools
---------
* **Matching**: Tools for pairing sets of geometries.
* **Affinity**: Functions to calculate similarity scores (e.g., IoU) between geometries.
* **Operations**: Core geometric manipulations (shifting, scaling, buffering) and queries.
* **Features**: Extraction of geometric properties.
* **Conversion**: Utilities to convert between `soundevent` geometries and `shapely` objects.
* **Visualisation**: Helpers for rendering geometries.
"""

from soundevent.geometry.affinity import (
    AffinityFn,
    compute_bbox_iou,
    compute_frequency_iou,
    compute_geometric_iou,
    compute_spectral_closeness,
    compute_temporal_closeness,
    compute_temporal_iou,
)
from soundevent.geometry.conversion import (
    geometry_to_shapely,
    shapely_to_geometry,
)
from soundevent.geometry.features import compute_geometric_features
from soundevent.geometry.match import (
    match_geometries_greedy,
    match_geometries_optimal,
    select_greedy_matches,
    select_optimal_matches,
)
from soundevent.geometry.operations import (
    buffer_geometry,
    compute_bbox_area,
    compute_bounds,
    compute_interval_overlap,
    compute_interval_width,
    get_geometry_point,
    get_point_in_frequency,
    get_point_in_time,
    group_sound_events,
    have_frequency_overlap,
    intervals_overlap,
    is_in_clip,
    rasterize,
    scale_geometry,
    shift_geometry,
)

__all__ = [
    "AffinityFn",
    "buffer_geometry",
    "compute_bbox_area",
    "compute_bbox_iou",
    "compute_bounds",
    "compute_frequency_iou",
    "compute_geometric_features",
    "compute_geometric_iou",
    "compute_interval_overlap",
    "compute_interval_width",
    "compute_spectral_closeness",
    "compute_temporal_closeness",
    "compute_temporal_iou",
    "geometry_to_shapely",
    "get_geometry_point",
    "get_point_in_frequency",
    "get_point_in_time",
    "group_sound_events",
    "have_frequency_overlap",
    "intervals_overlap",
    "is_in_clip",
    "match_geometries_greedy",
    "match_geometries_optimal",
    "rasterize",
    "scale_geometry",
    "select_greedy_matches",
    "select_optimal_matches",
    "shapely_to_geometry",
    "shift_geometry",
]
