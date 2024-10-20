"""Module for manipulation of xarray.DataArray objects.

This module provides functions for manipulating xarray.DataArray objects,
including creating range dimensions, setting dimension attributes, cropping and
extending axes, getting dimension ranges and widths, and setting values at
specific positions.
"""

from soundevent.arrays.attributes import ArrayAttrs, DimAttrs
from soundevent.arrays.dimensions import (
    Dimensions,
    create_frequency_dim_from_array,
    create_frequency_range,
    create_range_dim,
    create_time_dim_from_array,
    create_time_range,
    estimate_dim_step,
    get_coord_index,
    get_dim_range,
    get_dim_step,
    get_dim_width,
    set_dim_attrs,
)
from soundevent.arrays.operations import (
    adjust_dim_range,
    crop_dim,
    extend_dim,
    normalize,
    set_value_at_pos,
    to_db,
)

__all__ = [
    "ArrayAttrs",
    "DimAttrs",
    "Dimensions",
    "create_frequency_dim_from_array",
    "create_frequency_range",
    "create_range_dim",
    "create_time_dim_from_array",
    "create_time_range",
    "crop_dim",
    "estimate_dim_step",
    "extend_dim",
    "get_coord_index",
    "get_dim_range",
    "get_dim_step",
    "get_dim_width",
    "normalize",
    "set_dim_attrs",
    "set_value_at_pos",
    "to_db",
    "adjust_dim_range",
]
