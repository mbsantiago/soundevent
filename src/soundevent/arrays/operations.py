"""Module for manipulation of xarray.DataArray objects."""

from typing import Any, Callable, List, Optional, Union

import numpy as np
import xarray as xr
from numpy.typing import DTypeLike
from xarray.core.types import InterpOptions

from soundevent.arrays.dimensions import (
    create_range_dim,
    get_coord_index,
    get_dim_range,
    get_dim_step,
)

__all__ = [
    "center",
    "to_db",
    "crop_dim",
    "extend_dim",
    "normalize",
    "offset",
    "scale",
    "set_value_at_pos",
]


def crop_dim(
    arr: xr.DataArray,
    dim: str,
    start: Optional[float] = None,
    stop: Optional[float] = None,
    right_closed: bool = False,
    left_closed: bool = True,
    eps: float = 10e-6,
) -> xr.DataArray:
    """Crop a dimension of a data array to a specified range.

    Parameters
    ----------
    arr
        The input data array to crop.
    dim
        The name of the dimension to crop.
    start
        The start value of the cropped range. If None, the current start value
        of the axis is used. Defaults to None.
    stop
        The stop value of the cropped range. If None, the current stop value of
        the axis is used. Defaults to None.
    right_closed
        Whether the right boundary of the cropped range is closed.
        Defaults to False.
    left_closed
        Whether the left boundary of the cropped range is closed.
        Defaults to True.
    eps
        A small value added to start and subtracted from stop to ensure open
        intervals. Defaults to 10e-6.

    Returns
    -------
    xarray.DataArray
        The cropped data array.

    Raises
    ------
    ValueError
        If the coordinate for the specified dimension does not have 'start' and
        'stop' attributes, or if the specified range is outside the current
        axis range.

    Notes
    -----
    The function crops the specified dimension of the data array to the range
        [start, stop).
    The `right_closed` and `left_closed` parameters control whether the
        boundaries of the cropped range are closed or open.
    A small value `eps` is added to start and subtracted from stop to ensure
        open intervals if `right_closed` or `left_closed` is False.
    The 'start' and 'stop' attributes of the cropped dimension coordinate are
        updated accordingly.
    """
    current_start, current_stop = get_dim_range(arr, dim)

    if start is None:
        left_closed = True
        start = current_start

    if stop is None:
        right_closed = True
        stop = current_stop

    if start > stop:
        raise ValueError(
            f"Start value {start} must be less than stop value {stop}"
        )

    if start < current_start or stop > current_stop:
        raise ValueError(
            f"Cannot select axis '{dim}' from {start} to {stop}. "
            f"Axis range is {current_start} to {current_stop}"
        )

    slice_end = stop
    if not right_closed:
        slice_end = stop - eps

    slice_start = start
    if not left_closed:
        slice_start = start + eps

    return arr.sel({dim: slice(slice_start, slice_end)})


def extend_dim(
    arr: xr.DataArray,
    dim: str,
    start: Optional[float] = None,
    stop: Optional[float] = None,
    fill_value: float = 0,
    eps: float = 10e-6,
    left_closed: bool = True,
    right_closed: bool = False,
) -> xr.DataArray:
    """Extend a dimension of a data array to a specified range.

    Parameters
    ----------
    arr
        The input data array to extend.
    dim
        The name of the dimension to extend.
    start
        The start value of the extended range.
    stop
        The stop value of the extended range.
    fill_value
        The value to fill for missing data in the extended range.
        Defaults to 0.
    eps
        A small value added to start and subtracted from stop to ensure open
        intervals. Defaults to 10e-6.
    left_closed
        Whether the left boundary of the extended range is closed.
        Defaults to True.
    right_closed
        Whether the right boundary of the extended range is closed.
        Defaults to False.

    Returns
    -------
    xarray.DataArray
        The extended data array.

    Raises
    ------
    KeyError
        If the dimension is not found in the data array.

    Notes
    -----
    The function extends the specified dimension of the data array to the
        range [start, stop).
    If the specified range extends beyond the current axis range, the
        function adds values to the beginning or end of the coordinate
        array.
    The 'start' and 'stop' attributes of the extended dimension coordinate
        are updated accordingly.
    """
    coord = arr.coords[dim]
    coords = coord.data

    current_start, current_stop = get_dim_range(arr, dim)

    if start is None:
        start = current_start

    if stop is None:
        stop = current_stop

    if start > stop:
        raise ValueError(
            f"Start value {start} must be less than stop value {stop}"
        )

    step = get_dim_step(arr, dim)

    if left_closed:
        start -= eps

    if right_closed:
        stop += eps

    if start <= current_start - step:
        new_coords = np.arange(
            current_start - step,
            start,
            -step,
            dtype=coord.dtype,
        )[::-1]
        coords = np.concatenate([new_coords, coords])

    if stop >= current_stop:
        new_coords = np.arange(
            coords[-1],
            stop,
            step,
            dtype=coord.dtype,
        )[1:]
        coords = np.concatenate([coords, new_coords])

    arr = arr.reindex(
        {dim: coords},
        fill_value=fill_value,  # type: ignore
    )

    arr.coords[dim].attrs.update(
        start=start,
        stop=stop,
    )

    return arr


def set_value_at_pos(
    array: xr.DataArray,
    value: Any,
    **query,
) -> xr.DataArray:
    """Set a value at a specific position in a data array.

    Parameters
    ----------
    array
        The input data array.
    value
        The value to set at the specified position.
    **query : dict
        Keyword arguments specifying the position in each dimension where the
        value should be set. Keys are dimension names, values are the
        positions.

    Returns
    -------
    xarray.DataArray
        The modified data array with the value set at the specified position.

    Raises
    ------
    ValueError
        If a dimension specified in the query is not found in the data array.
    KeyError
        If the position specified in the query is outside the range of the
        corresponding dimension.

    Notes
    -----
    Modifies the input data array in-place.

    When specifying approximate positions (e.g., `x=1.5`) the value will be set
    at the closest coordinate to the left of the specified value.
    This aligns with how coordinates are often interpreted as the
    boundaries of intervals.

    If `value` is a tuple or list, its dimensions must match the queried
    dimensions of the array, and the value will be set at the specified
    position along each dimension.

    Examples
    --------
    >>> import xarray as xr
    >>> import numpy as np
    >>> data = np.zeros((3, 3))
    >>> coords = {"x": np.arange(3), "y": np.arange(3)}
    >>> array = xr.DataArray(data, coords=coords, dims=("x", "y"))

    Setting a single value:
    >>> array = set_value_at_position(array, 1, x=1, y=1)
    >>> print(array)
    <xarray.DataArray (x: 3, y: 3)>
    array([[0., 0., 0.],
           [0., 1., 0.],
           [0., 0., 0.]])

    Setting a value at an approximate position:
    >>> array = xr.DataArray(data, coords=coords, dims=("x", "y"))
    >>> array = set_value_at_position(array, 1, x=1.5, y=1.5)
    >>> print(array)
    <xarray.DataArray (x: 3, y: 3)>
    array([[0., 0., 0.],
           [0., 1., 0.],
           [0., 0., 0.]])

    Setting a multi-dimensional value:
    >>> array = xr.DataArray(data, coords=coords, dims=("x", "y"))
    >>> value = np.array([1, 2, 3])
    >>> array = set_value_at_position(array, value, x=1)
    >>> print(array)
    <xarray.DataArray (x: 3, y: 3)>
    array([[0., 0., 0.],
           [1., 2., 3.],
           [0., 0., 0.]])
    """
    indexer: List[Union[slice, int]] = [slice(None) for _ in range(array.ndim)]

    for dim, coord in query.items():
        dim_index: int = array.get_axis_num(dim)  # type: ignore
        indexer[dim_index] = get_coord_index(array, dim, coord)

    if isinstance(value, (tuple, list)):
        coord = np.array(value)

    array.data[tuple(indexer)] = value
    return array


def offset(
    arr: xr.DataArray,
    val: float,
) -> xr.DataArray:
    """Offset the values of a data array by a constant value.

    Parameters
    ----------
    arr
        The input data array to offset.
    val
        The value to add to the data array.

    Returns
    -------
    xarray.DataArray
        The offset data array.

    Notes
    -----
    This function stores the offset used for the offsetting as an attribute in
    the output data array.
    """
    with xr.set_options(keep_attrs=True):
        return (arr + val).assign_attrs(add_offset=-val)


def scale(arr: xr.DataArray, val: float) -> xr.DataArray:
    """Scale the values of a data array by a constant value.

    Parameters
    ----------
    arr
        The input data array to scale.
    val
        The value to multiply the data array by.

    Returns
    -------
    xarray.DataArray
        The scaled data array.

    Notes
    -----
    This function stores the scale factor used for scaling as an attribute in
    the output data array.
    """
    with xr.set_options(keep_attrs=True):
        return (arr * val).assign_attrs(scale_factor=1 / val)


def normalize(
    arr: xr.DataArray,
) -> xr.DataArray:
    """Normalize the values of a data array to the range [0, 1].

    Parameters
    ----------
    arr
        The input data array to normalize.

    Returns
    -------
    xarray.DataArray
        The normalized data array.

    Notes
    -----
    This function stores the offset and scale factor used for normalization as
    attributes in the output data array.
    """
    offset_val = arr.min().item()
    scale_val = arr.max().item() - offset_val

    if scale_val == 0:
        return offset(arr, -offset_val)

    arr = offset(arr, -offset_val)
    return scale(arr, 1 / scale_val)


def center(
    arr: xr.DataArray,
) -> xr.DataArray:
    """Center the values of a data array around zero.

    Parameters
    ----------
    arr
        The input data array to center.

    Returns
    -------
    xarray.DataArray
        The centered data array.

    Notes
    -----
    This function stores the offset used for centering as an attribute in the
    output data array.
    """
    return offset(arr, -arr.mean().item())


def resize(
    arr: xr.DataArray,
    method: InterpOptions = "linear",
    dtype: DTypeLike = np.float64,
    **dims: int,
) -> xr.DataArray:
    """Resize a data array to the specified dimensions.

    Parameters
    ----------
    arr
        The input data array to resize.
    method
        The interpolation method to use. Defaults to 'linear'.
    dtype
        The data type of the resized data array. Defaults to np.float64.
    **dims
        The new dimensions for each axis of the data array.

    Returns
    -------
    xarray.DataArray
        The resized data array.

    Raises
    ------
    ValueError
        If the new dimensions do not match the current dimensions of the data
        array.

    Notes
    -----
    This function resizes the data array to the specified dimensions. The
    function does not modify the data array in place.
    """
    new_coords = {}

    for dim, size in dims.items():
        if dim not in arr.dims:
            raise ValueError(f"Dimension {dim} not found in array.")

        step = get_dim_step(arr, dim)
        start, stop = get_dim_range(arr, dim)

        new_coords[dim] = create_range_dim(
            name=dim,
            start=start,
            stop=stop + step,
            size=size,
            dtype=dtype,
        )

    return arr.interp(coords=new_coords, method=method)


def to_db(
    arr: xr.DataArray,
    ref: Union[float, Callable[[xr.DataArray], float]] = 1.0,
    amin: float = 1e-10,
    min_db: Optional[float] = -80.0,
    max_db: Optional[float] = None,
    power: int = 1,
) -> xr.DataArray:
    """Compute the decibel values of a data array.

    Parameters
    ----------
    arr
        The input data array.
    ref
        The reference value for the decibel computation. Defaults to 1.0.
    amin
        Minimum threshold for the input data array. Defaults to 1e-10. All
        values below this threshold are replaced with this value before
        computing the decibel values.
    min_db
        The minimum decibel value for the output data array. Defaults to 80.0.
        All values below this threshold are replaced with this value. If None,
        no minimum threshold is applied.
    max_db
        The maximum decibel value for the output data array. Defaults to None.
        All values above this threshold are replaced with this value. If None,
        no maximum threshold is applied.

    Returns
    -------
    xarray.DataArray
        The data array with decibel values computed.

    Notes
    -----
    The function computes the decibel values of the input data array using the
    formula 10 * log10(arr / ref).

    This function is heavily inspired by and includes modifications of code
    originally found in librosa, available at
    https://github.com/librosa/librosa/.
    The original code is licensed under the ISC license.

    Original copyright notice:
    Copyright (c) 2013--2023, librosa development team.

    Permission to use, copy, modify, and/or distribute this software for any
    purpose with or without fee is hereby granted, provided that the above
    copyright notice and this permission notice appear in all copies.

    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
    SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR
    IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
    """
    if amin < 0:
        raise ValueError("amin must be greater than 0.")

    if callable(ref):
        ref = ref(arr)

    if ref <= 0:
        raise ValueError("ref must be greater than 0.")

    a_arr = np.maximum(np.power(amin, 1 / power), arr)
    a_ref = np.maximum(np.power(amin, 1 / power), np.power(ref, 1 / power))

    data = 10.0 * power * np.log10(a_arr) - 10.0 * power * np.log10(a_ref)

    if min_db is not None:
        data = np.maximum(data, min_db)

    if max_db is not None:
        data = np.minimum(data, max_db)

    # Update units to reflect the decibel values
    attrs = arr.attrs.copy()
    new_units = "dB" if "units" not in attrs else f"{attrs['units']} dB"
    attrs["units"] = new_units

    return xr.DataArray(
        data=data,
        dims=arr.dims,
        coords=arr.coords,
        attrs=attrs,
    )
