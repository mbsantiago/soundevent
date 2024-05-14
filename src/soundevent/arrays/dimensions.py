"""Creating and manipulating DataArray dimensions in computational acoustics.

This module provides functions to:

* **Define standard dimensions:**  Quickly create common dimensions in
computational acoustics like 'time', 'frequency', 'channel', 'category', and
'feature' using the `Dimensions` enumeration.

* **Build flexible data structures:**  Construct range-based dimensions
(e.g., for time or frequency) with desired start, stop, and step values
using `create_range_dim`.

* **Work with time series:**  Generate time dimensions from arrays or given
parameters with `create_time_range` and `create_time_dim_from_array`.

* **Handle frequency representations:**  Create frequency dimensions from
arrays or specified ranges with  `create_frequency_range` and
`create_frequency_dim_from_array`.

* **Modify and extract metadata:**  Set dimension attributes
(`set_dim_attrs`), retrieve dimension ranges (`get_dim_range`), calculate
dimension width (`get_dim_width`), and estimate dimension step size
(`get_dim_step`).

"""

from enum import Enum
from typing import Optional, Tuple

import numpy as np
import xarray as xr
from numpy.typing import DTypeLike

from soundevent.arrays.attributes import DimAttrs

__all__ = [
    "Dimensions",
    "create_frequency_dim_from_array",
    "create_frequency_range",
    "create_range_dim",
    "create_time_dim_from_array",
    "create_time_range",
    "estimate_dim_step",
    "get_dim_range",
    "get_dim_step",
    "get_dim_width",
    "set_dim_attrs",
    "get_coord_index",
]

TIME_UNITS = "s"
TIME_STANDARD_NAME = "time"
TIME_LONG_NAME = "Time since start of recording"

FREQUENCY_UNITS = "Hz"
FREQUENCY_STANDARD_NAME = "frequency"
FREQUENCY_LONG_NAME = "Frequency"


class Dimensions(str, Enum):
    """Defines standard dimension names for computational acoustics arrays.

    This enumeration provides convenient and descriptive names for dimensions
    essential to representing acoustic data

    Notes
    -----
    Use these dimension names to ensure consistency and clarity in your code.
    """

    time = "time"
    """Name for the time dimension of an array.

    This dimension represents time in seconds and should monotonically increase
    from the start to the end of the array. While generally regularly spaced,
    it may contain missing values or irregular spacing in special cases.
    """

    frequency = "frequency"
    """Name for the frequency dimension of an array.

    This dimension represents frequency in Hz and should monotonically increase
    from the start to the end of the array. Generally regularly spaced, it may
    contain irregular spacing, such as with a logarithmic frequency scale or
    custom frequency bins.
    """

    channel = "channel"
    """Name for the channel dimension of an array.

    This dimension represents the channel number of a multi-channel array,
    typically used in multi-channel audio recordings or spectrograms. Each
    channel corresponds to a distinct audio source or microphone in the
    recording.
    """

    category = "category"
    """Name for the category dimension of an array.

    This dimension represents a categorical variable or label for each element
    in the array. If the original data is not categorical, it's converted
    to categorical data. Each value should be a string or integer label
    corresponding to a category or class.
    """

    feature = "feature"
    """Name for the feature dimension of an array.

    This dimension represents a feature or numerical descriptor of the data.
    It's not limited to feature extraction results but can also include
    hand-measured or derived features. If an array contains multiple features,
    each feature should be stored along this dimension, with the name of
    the feature stored as a coordinate variable. If the array has time and
    frequency dimensions, the feature dimension then represents the feature
    values at each time-frequency point.
    """


def create_range_dim(
    name: str,
    start: float,
    stop: float,
    step: Optional[float] = None,
    size: Optional[int] = None,
    dtype: DTypeLike = np.float64,
    **attrs,
) -> xr.Variable:
    """Create a range dimension.

    Most coordinates used in computational bioacoustics are regularly spaced
    ranges. This function creates a range dimension with a specified start,
    stop, and step size. It stores the start, end, and step values as attributes
    on the coordinate.

    Parameters
    ----------
    name : str
        The name of the range dimension.
    start : float
        The start value of the range.
    stop : float
        The stop value of the range.
    step : float
        The step size between values in the range.
    dtype : numpy.dtype or str, optional
        The data type of the values in the range.
        Defaults to np.float32.
    **attrs
        Additional attributes to store on the range dimension.

    Returns
    -------
    xarray.Variable
        A variable representing the range dimension.

    Notes
    -----
    - The range is created using np.arange(start, stop, step, dtype).
    - The variable has attributes 'start', 'end', and 'step' representing the
        range parameters.
    """
    if step is None:
        if size is None:
            raise ValueError("Either step or size must be provided.")

        step = (stop - start) / size

    coords = np.arange(
        start=start,
        stop=stop,
        step=step,
        dtype=dtype,
    )

    # NOTE: Remove the last element if it is greater than or equal to the stop
    # value. This is necessary because np.arange includes the stop value if
    # it is an exact multiple of the step size, but we want to exclude it.
    if coords[-1] >= stop - step / 2:
        coords = coords[:-1]

    return xr.Variable(
        dims=name,
        data=coords,
        attrs={
            DimAttrs.step.value: step,
            **attrs,
        },
    )


def create_time_range(
    start_time: float,
    end_time: float,
    step: Optional[float] = None,
    samplerate: Optional[float] = None,
    name: str = Dimensions.time.value,
    dtype: DTypeLike = np.float64,
    **attrs,
) -> xr.Variable:
    """Generate an xarray Variable representing a time range dimension.

    Creates a time range with specified start (in seconds), end (in seconds),
    and the desired time step between values.

    Parameters
    ----------
    start_time
        Start of the time range (in seconds).
    end_time
        End of the time range (in seconds).
    step
        Step size between time values (in seconds). If not provided,
         calculated as 1 / samplerate.
    samplerate
        Sampling rate (in Hz). Used to calculate step if step is not given.
         If both step and samplerate are provided, step takes precedence.
    name
        Name of the time dimension. Defaults to 'time'.
    dtype: NumPy-like dtype
        Data type of the time values. Defaults to np.float64.
    **attrs
        Additional attributes for the xarray Variable.

    Returns
    -------
    xarray.Variable
        Variable containing the time range values.
    """
    if step is None:
        if samplerate is None:
            raise ValueError("Either step or samplerate must be provided.")

        step = 1.0 / samplerate

    return create_range_dim(
        name=name,
        start=start_time,
        stop=end_time,
        step=step,
        dtype=dtype,
        **{
            DimAttrs.units.value: TIME_UNITS,
            DimAttrs.standard_name.value: TIME_STANDARD_NAME,
            DimAttrs.long_name.value: TIME_LONG_NAME,
            **attrs,
        },
    )


def create_frequency_range(
    low_freq: float,
    high_freq: float,
    step: float,
    name: str = Dimensions.frequency.value,
    dtype: DTypeLike = np.float64,
    **attrs,
) -> xr.Variable:
    """Generate an xarray Variable representing a frequency range dimension.

    Creates a frequency range with a specified start (in Hz), end (in Hz),
     and step size (in Hz).

    Parameters
    ----------
    low_freq: float
        Start of the frequency range (in Hz).
    high_freq: float
        End of the frequency range (in Hz).
    step: float
        Step size between frequency values (in Hz).
    name: str
        Name of the frequency dimension. Defaults to 'frequency'.
    dtype: NumPy-like dtype
        Data type of the frequency values. Defaults to np.float64.
    **attrs
        Additional attributes for the xarray Variable.

    Returns
    -------
    xarray.Variable
        Variable containing the frequency range values.
    """
    return create_range_dim(
        name=name,
        start=low_freq,
        stop=high_freq,
        step=step,
        dtype=dtype,
        **{
            DimAttrs.units.value: FREQUENCY_UNITS,
            DimAttrs.standard_name.value: FREQUENCY_STANDARD_NAME,
            DimAttrs.long_name.value: FREQUENCY_LONG_NAME,
            **attrs,
        },
    )


def set_dim_attrs(
    array: xr.DataArray,
    dim: str,
    **attrs,
) -> xr.DataArray:
    """Set the range of a dimension in a data array.

    Use this function to set the precise start and end values of a dimension
    in a data array. This is useful when the coordinates represent the start
    of a range, but you want to specify the end of the range as well.

    The start and end values are stored as attributes on the coordinates.
    """
    coords = array.coords[dim]
    coords.attrs.update(attrs)
    return array


def get_dim_range(
    array: xr.DataArray,
    dim: str,
) -> Tuple[float, float]:
    """Get the range of a dimension in a data array.

    Parameters
    ----------
    array : xarray.DataArray
        The data array from which to extract the dimension range.
    dim : str
        The name of the dimension.

    Returns
    -------
    Tuple[Optional[float], Optional[float]]
        A tuple containing the start and end values of the dimension range.

    Raises
    ------
    KeyError
        If the dimension is not found in the data array.
    """
    index = array.indexes[dim]
    return index.min(), index.max()


def get_dim_width(arr: xr.DataArray, dim: str) -> float:
    """Get the width of a dimension in a data array.

    Parameters
    ----------
    arr
        The data array containing the dimension.
    dim
        The name of the dimension.

    Returns
    -------
    float
        The width of the dimension.

    Raises
    ------
    KeyError
        If the dimension is not found in the data array.
    """
    start, end = get_dim_range(arr, dim)
    return float(end - start)


def estimate_dim_step(
    data: np.ndarray,
    rtol: float = 1.0e-5,
    atol: float = 1.0e-8,
    check_tolerance: bool = True,
) -> float:
    """Estimate the step size of a numerical array.

    Parameters
    ----------
    data
        The numerical array.
    rtol
        The relative tolerance used when checking if all values are within a
        specified range of the mean step size. Defaults to 1e-5.
    atol
        The absolute tolerance used when checking if all values are within a
        specified range of the mean step size. Defaults to 1e-8.
    check_tolerance
        A flag indicating whether to perform a tolerance check on the differences
        between consecutive values. If True (default), raises a ValueError if
        the differences exceed the specified tolerances.

    Returns
    -------
    float
        The estimated step size of the array.

    Raises
    ------
    ValueError
        If `check_tolerance` is True and the differences between consecutive
        values exceed the specified tolerances (indicating an irregular step size).

    Notes
    -----
    This function calculates the mean of the differences between consecutive
    values in the array. If `check_tolerance` is True, it verifies if all
    differences are within a specified tolerance (defined by `rtol` and `atol`)
    of the calculated mean step size. If not, it raises a `ValueError` indicating
    an irregular step size.

    This function assumes the array values are numerical and equidistant
    (constant step size) unless the tolerance check fails.
    """
    steps = np.diff(data)
    mean_step = steps.mean()

    if (
        check_tolerance
        and not np.isclose(
            steps,
            mean_step,
            rtol=rtol,
            atol=atol,
        ).all()
    ):
        raise ValueError("Array values do not have a consistent step size.")

    return mean_step


def get_dim_step(
    arr: xr.DataArray,
    dim: str,
    rtol: float = 1.0e-5,
    atol: float = 1.0e-8,
    check_tolerance: bool = True,
    estimate_step: bool = True,
) -> float:
    """Calculate the step size between values along a dimension in a DataArray.

    Parameters
    ----------
    arr : xr.DataArray
        The input DataArray.
    dim : str
        The name of the dimension for which to calculate the step size.
    rtol : float, optional
        The relative tolerance used when checking if all coordinate differences
        are within a specified range of the mean step size. Defaults to 1e-5.
    atol : float, optional
        The absolute tolerance used when checking if all coordinate differences
        are within a specified range of the mean step size. Defaults to 1e-8.
    check_tolerance : bool, optional
        A flag indicating whether to perform a tolerance check on the coordinate
        differences. If True (default), raises a ValueError if the differences
        exceed the specified tolerances.
    estimate_step : bool, optional
        A flag indicating whether to estimate the step size if not present in
        the dimension attributes. If True (default), calculates the mean step
        size from the coordinate values. Otherwise, raises a ValueError if the
        step size is not found in the dimension attributes.

    Returns
    -------
    float
        The calculated step size (spacing) between consecutive values along the
        specified dimension.

    Raises
    ------
    ValueError
        If `check_tolerance` is True and the coordinate differences exceed
        the specified tolerances (indicating an irregular step size).

    Notes
    -----
    This function first attempts to retrieve the step size from the dimension's
    attributes using the standard attribute name `'step'` defined in the
    `RangeAttrs` enumeration. If the attribute is not present, it calculates
    the step size by taking the mean of the differences between consecutive
    coordinate values.

    If `check_tolerance` is True, the function verifies if all coordinate
    differences are within a specified tolerance (defined by `rtol` and `atol`)
    of the calculated mean step size. If not, it raises a `ValueError`
    indicating an irregular step size.

    This function assumes the DataArray coordinates are numerical and
    equidistant (constant step size) unless a valid step size attribute
    is present or the tolerance check fails.
    """
    coord = arr.coords[dim]
    attrs = coord.attrs

    if DimAttrs.step.value in attrs:
        return attrs[DimAttrs.step.value]

    if not estimate_step:
        raise ValueError(
            f"Step size not found in the '{dim}' dimension attributes."
        )

    return estimate_dim_step(
        coord.data,
        rtol=rtol,
        atol=atol,
        check_tolerance=check_tolerance,
    )


def create_time_dim_from_array(
    coods: np.ndarray,
    name: str = Dimensions.time.value,
    dtype: Optional[DTypeLike] = None,
    step: Optional[float] = None,
    samplerate: Optional[float] = None,
    estimate_step: bool = False,
    **kwargs,
) -> xr.Variable:
    """Create a time dimension from an array of time values.

    Parameters
    ----------
    coods
        The time values.
    name
        The name of the time dimension.
    dtype
        The data type of the time values. If None, the data type is inferred
        from the input array.
    **kwargs
        Additional attributes to store on the time dimension.

    Returns
    -------
    xarray.Variable
        The time dimension variable.
    """
    if dtype is None:
        dtype = coods.dtype

    if samplerate is not None:
        step = 1 / samplerate

    if estimate_step and step is None:
        step = estimate_dim_step(coods)

    attrs = {
        DimAttrs.units.value: TIME_UNITS,
        DimAttrs.standard_name.value: TIME_STANDARD_NAME,
        DimAttrs.long_name.value: TIME_LONG_NAME,
        **kwargs,
    }

    if step is not None:
        attrs[DimAttrs.step.value] = step

    return xr.Variable(
        dims=name,
        data=coods,
        attrs=attrs,
    )


def create_frequency_dim_from_array(
    coods: np.ndarray,
    name: str = Dimensions.frequency.value,
    step: Optional[float] = None,
    estimate_step: bool = False,
    dtype: Optional[DTypeLike] = None,
    **kwargs,
) -> xr.Variable:
    """Create a frequency dimension from an array of frequency values.

    Parameters
    ----------
    coods
        The frequency values.
    name
        The name of the frequency dimension.
    dtype
        The data type of the frequency values. If None, the data type is inferred
        from the input array.
    **kwargs
        Additional attributes to store on the frequency dimension.

    Returns
    -------
    xarray.Variable
        The frequency dimension variable.
    """
    if dtype is None:
        dtype = coods.dtype

    if estimate_step and step is None:
        step = estimate_dim_step(coods)

    attrs = {
        DimAttrs.units.value: FREQUENCY_UNITS,
        DimAttrs.standard_name.value: FREQUENCY_STANDARD_NAME,
        DimAttrs.long_name.value: FREQUENCY_LONG_NAME,
        **kwargs,
    }

    if step is not None:
        attrs[DimAttrs.step.value] = step

    return xr.Variable(
        dims=name,
        data=coods,
        attrs=attrs,
    )


def get_coord_index(
    arr: xr.DataArray,
    dim: str,
    value: float,
    raise_error: bool = True,
) -> int:
    """Get the index of a value along a dimension in a DataArray.

    Parameters
    ----------
    arr : xr.DataArray
        The input DataArray.
    dim : str
        The name of the dimension.
    value : float
        The value to find along the dimension.
    raise_error: bool, optional
        A flag indicating whether to raise an error if the value is outside
        the range of the dimension. If True (default), raises a KeyError.
        If False, returns the index of the closest value within the range.

    Returns
    -------
    int
        The index of the value along the specified dimension.

    Raises
    ------
    ValueError
        If the value is not found within the range of the dimension or if the
        dimension is not found in the DataArray.
    """
    start, stop = get_dim_range(arr, dim)

    if value < start or value > stop:
        if raise_error:
            raise KeyError(
                f"Position {value} is outside the range of dimension {dim}."
            )

        if value < start:
            return 0

        return arr.sizes[dim]

    index = arr.indexes[dim].get_slice_bound(value, "right")
    return index - 1
