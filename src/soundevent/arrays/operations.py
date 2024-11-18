"""Module for manipulation of xarray.DataArray objects."""

from typing import Any, Callable, List, Literal, Optional, Union

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
    "adjust_dim_range",
    "resize",
    "crop_dim_width",
    "extend_dim_width",
    "adjust_dim_width",
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


def adjust_dim_range(
    array: xr.DataArray,
    dim: str,
    start: Optional[float] = None,
    stop: Optional[float] = None,
    fill_value: float = 0,
) -> xr.DataArray:
    """Adjust the range of a specified dimension in an xarray DataArray.

    This function modifies the range of a given dimension (`dim`) in an
    xarray DataArray to match a desired range defined by `start` and
    `stop`. It ensures that the adjusted dimension aligns with these
    bounds while considering the original step size of the dimension.

    Parameters
    ----------
    array : xr.DataArray
        The input xarray DataArray to be adjusted.
    dim : str
        The name of the dimension to be adjusted.
    start : float, optional
        The desired starting value for the dimension. If None (default),
        the starting value is not adjusted.
    stop : float, optional
        The desired stopping value for the dimension. If None (default),
        the stopping value is not adjusted.
    fill_value : float, optional
        The value to fill for missing data in the extended range. Defaults
        to 0.

    Returns
    -------
    xr.DataArray
        The adjusted xarray DataArray with the modified dimension range.

    Raises
    ------
    ValueError
        - If both `start` and `stop` are None.
        - If `start` is greater than or equal to `stop`.

    Notes
    -----
    The function utilizes `crop_dim` and `extend_dim` to modify the
    specified dimension. It calculates adjusted bounds to ensure the
    modified dimension aligns with the desired range while preserving
    the original step size as much as possible.
    """
    if start is None and stop is None:
        raise ValueError("At least one of start and stop must be specified.")

    if start is not None and stop is not None and start >= stop:
        raise ValueError("start must be less than stop.")

    step = get_dim_step(array, dim)

    if start is not None:
        target_start = np.floor(start / step) * step
        spec_start = array.coords[dim].min()
        if spec_start < start:
            array = crop_dim(
                array,
                dim,
                start=target_start,
            )
        elif spec_start > start:
            array = extend_dim(
                array,
                dim,
                start=target_start,
                fill_value=fill_value,
            )

    if stop is not None:
        target_stop = np.floor(stop / step) * step
        spec_stop = array.coords[dim].max()
        if spec_stop < stop:
            array = extend_dim(
                array,
                dim,
                stop=target_stop,
                fill_value=fill_value,
                right_closed=True,
            )
        elif spec_stop > stop:
            array = crop_dim(
                array,
                dim,
                stop=target_stop,
                right_closed=True,
            )

    return array


Position = Literal["start", "center", "end"]


def crop_dim_width(
    array: xr.DataArray,
    dim: str,
    width: int,
    position: Position = "start",
) -> xr.DataArray:
    """Crops an xarray DataArray along a specified dimension to a given width.

    Parameters
    ----------
    array : xr.DataArray
        The DataArray to be cropped.
    dim : str
        The name of the dimension to crop.
    width : int
        The desired width of the dimension after cropping.
    position : {'start', 'end', 'center'}, default: 'start'
        The position from which to crop.
        - 'start': Crop from the beginning of the dimension.
        - 'end': Crop from the end of the dimension.
        - 'center': Crop from the center of the dimension.

    Returns
    -------
    xr.DataArray
        The cropped DataArray.

    Raises
    ------
    ValueError
        If the new width is greater than or equal to the current width,
        or if the position is invalid.

    Examples
    --------
    >>> import xarray as xr
    >>> import numpy as np
    >>> array = xr.DataArray(np.arange(10), dims="x")
    >>> crop_dim_width(array, "x", 5, position="start")
    <xarray.DataArray (x: 5)>
    array([0, 1, 2, 3, 4])
    Coordinates:
      * x        (x) int64 0 1 2 3 4
    >>> crop_dim_width(array, "x", 3, position="end")
    <xarray.DataArray (x: 3)>
    array([7, 8, 9])
    Coordinates:
      * x        (x) int64 7 8 9
    >>> crop_dim_width(array, "x", 4, position="center")
    <xarray.DataArray (x: 4)>
    array([3, 4, 5, 6])
    Coordinates:
      * x        (x) int64 3 4 5 6
    """
    if width >= array.sizes[dim]:
        raise ValueError("New width must be less than current width.")

    if position == "start":
        coords = array.coords[dim].data[:width]
    elif position == "end":
        coords = array.coords[dim].data[-width:]
    elif position == "center":
        start = max(0, array.sizes[dim] // 2 - width // 2)
        coords = array.coords[dim].data[start : start + width]
    else:
        raise ValueError(f"Invalid position: {position}")  # type: ignore

    return array.sel({dim: coords})


def extend_dim_width(
    array: xr.DataArray,
    dim: str,
    width: int,
    fill_value: float = 0,
    position: Position = "start",
) -> xr.DataArray:
    """Extend an xarray DataArray along a specified dimension to a given width.

    Parameters
    ----------
    array : xr.DataArray
        The DataArray to be extended.
    dim : str
        The name of the dimension to extend.
    width : int
        The desired width of the dimension after extension.
    fill_value : float, default: 0
        The value to fill the extended region with.
    position : {'start', 'end', 'center'}, default: 'start'
        The position at which to extend. Imagine placing the original array
        within a larger array of the desired width. This parameter controls
        where the original array is placed within this larger array:

        - 'start': Keep the start position of the original array, and extend
          towards the end of the larger array.
        - 'end': Keep the end position of the original array, and extend
          towards the start of the larger array.
        - 'center': Extend at both ends of the original array, keeping it
          centered within the larger array.

    Returns
    -------
    xr.DataArray
        The extended DataArray.

    Raises
    ------
    ValueError
        If the new width is less than or equal to the current width,
        or if the position is invalid.

    Examples
    --------
    >>> import xarray as xr
    >>> import numpy as np
    >>> array = xr.DataArray(np.arange(5), dims="x")
    >>> extend_dim_width(array, "x", 8, position="start")
    <xarray.DataArray (x: 8)>
    array([0., 1., 2., 3., 4., 0., 0., 0.])
    Coordinates:
      * x        (x) float64 0.0 1.0 2.0 3.0 4.0 5.0 6.0 7.0
    >>> extend_dim_width(array, "x", 7, position="end")
    <xarray.DataArray (x: 7)>
    array([0., 0., 0., 1., 2., 3., 4.])
    Coordinates:
      * x        (x) int64 -2 -1  0  1  2  3  4
    >>> extend_dim_width(array, "x", 9, position="center")
    <xarray.DataArray (x: 9)>
    array([0., 0., 0., 1., 2., 3., 4., 0., 0.])
    Coordinates:
      * x        (x) float64 -2.0 -1.0 0.0 1.0 2.0 3.0 4.0 5.0 6.0
    """
    coords = array.coords[dim].data
    step = get_dim_step(array, dim)

    current_width = len(coords)
    current_start = coords[0]
    current_end = coords[-1]

    if current_width >= width:
        raise ValueError("New width must be greater than current width.")

    if position == "start":
        extra_width = width - current_width
        new_coords = np.arange(
            current_end + step,
            current_end + step + extra_width * step,
            step,
            dtype=coords.dtype,
        )
        coords = np.concatenate([coords, new_coords])

    elif position == "end":
        extra_width = width - current_width
        new_coords = np.arange(
            current_start - step,
            current_start - step - extra_width * step,
            -step,
            dtype=coords.dtype,
        )[::-1]
        coords = np.concatenate([new_coords, coords])

    elif position == "center":
        extra_width = width - current_width
        extra_start = extra_width // 2
        extra_end = extra_width - extra_start

        new_coords_start = np.arange(
            current_start - step,
            current_start - step - extra_start * step,
            -step,
            dtype=coords.dtype,
        )[::-1]

        new_coords_end = np.arange(
            current_end + step,
            current_end + step + extra_end * step,
            step,
            dtype=coords.dtype,
        )

        coords = np.concatenate([new_coords_start, coords, new_coords_end])

    else:
        raise ValueError(f"Invalid position: {position}")

    return array.reindex(
        {dim: coords},
        fill_value=fill_value,  # type: ignore
    )


def adjust_dim_width(
    array: xr.DataArray,
    dim: str,
    width: int,
    fill_value: float = 0,
    position: Position = "start",
) -> xr.DataArray:
    """Adjust the width of an xarray DataArray along a specified dimension.

    This function effectively places the original array within a larger or
    smaller array of the desired width (`width`), cropping or extending it as
    needed. The `position` parameter controls where the original array is
    placed within this other array:

    - 'start': Places the input array at the start, cropping or extending
      towards the end.
    - 'end': Places the input array at the end, cropping or extending
      towards the start.
    - 'center': Places the input array at the center, cropping or extending
      at both ends.

    Parameters
    ----------
    array : xr.DataArray
        The DataArray to be adjusted.
    dim : str
        The name of the dimension to adjust.
    width : int
        The desired width of the dimension.
    fill_value : float, default: 0
        The value to fill the extended region with, if extending.
    position : {'start', 'end', 'center'}, default: 'start'
        The position from which to crop or at which to extend.
        - 'start': Crop/extend at the beginning of the dimension.
        - 'end': Crop/extend at the end of the dimension.
        - 'center': Crop/extend at the center of the dimension.

    Returns
    -------
    xr.DataArray
        The adjusted DataArray.

    Raises
    ------
    ValueError
        If the width is less than 1.

    Examples
    --------
    >>> import xarray as xr
    >>> import numpy as np
    >>> array = xr.DataArray(np.arange(10), dims="x")
    >>> adjust_dim_width(array, "x", 5, position="start")
    <xarray.DataArray (x: 5)>
    array([0, 1, 2, 3, 4])
    Coordinates:
      * x        (x) int64 0 1 2 3 4
    >>> adjust_dim_width(array, "x", 12, position="end")
    <xarray.DataArray (x: 12)>
    array([0., 0., 0., 1., 2., 3., 4., 5., 6., 7., 8., 9.])
    Coordinates:
      * x        (x) float64 -2.0 -1.0 0.0 1.0 2.0 3.0 ... 6.0 7.0 8.0 9.0 10.0
    """
    if width < 1:
        raise ValueError("Width must be greater than or equal to 1.")

    current_width = array.sizes[dim]
    if width == current_width:
        return array

    if width < current_width:
        return crop_dim_width(array, dim, width, position=position)

    return extend_dim_width(
        array,
        dim,
        width,
        fill_value=fill_value,
        position=position,
    )
