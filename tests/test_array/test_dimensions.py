"""Test suite for soundevent.arrays.dimensions module."""

import numpy as np
import pytest
import xarray as xr

from soundevent import arrays


def test_create_time_range_has_correct_attrs():
    """Test create_time_range function."""
    time_range = arrays.create_time_range(start_time=0, end_time=10, step=10)
    assert time_range.attrs["units"] == "s"
    assert time_range.attrs["long_name"] == "Time since start of recording"
    assert time_range.attrs["standard_name"] == "time"


def test_create_time_range_with_step():
    """Test create_time_range_with_step function."""
    time_range = arrays.create_time_range(start_time=0, end_time=10, step=1)
    assert isinstance(time_range, xr.Variable)
    assert time_range.shape == (10,)
    assert time_range.data.tolist() == list(range(0, 10))
    assert time_range.attrs["step"] == 1


def test_create_time_range_with_samplerate():
    """Test create_time_range_with_samplerate function."""
    time_range = arrays.create_time_range(
        start_time=0,
        end_time=10,
        samplerate=100,
    )
    assert isinstance(time_range, xr.Variable)
    assert time_range.shape == (1000,)
    assert time_range.data.tolist() == [0.01 * i for i in range(1000)]
    assert time_range.attrs["step"] == 0.01


def test_create_frequency_range_has_correct_attrs():
    """Test create_frequency_range function."""
    frequency_range = arrays.create_frequency_range(
        low_freq=0,
        high_freq=1000,
        step=100,
    )
    assert frequency_range.attrs["units"] == "Hz"
    assert frequency_range.attrs["long_name"] == "Frequency"
    assert frequency_range.attrs["standard_name"] == "frequency"
    assert frequency_range.attrs["step"] == 100


def test_create_frequency_range_with_step():
    """Test create_frequency_range_with_step function."""
    frequency_range = arrays.create_frequency_range(
        low_freq=0,
        high_freq=1000,
        step=100,
    )
    assert isinstance(frequency_range, xr.Variable)
    assert frequency_range.shape == (10,)
    assert frequency_range.data.tolist() == list(range(0, 1000, 100))


def test_set_dim_attrs_is_succesful():
    """Test set_dim_attrs function."""
    arr = xr.DataArray(
        [1, 2, 3],
        dims=("x",),
        coords={"x": [0, 1, 2]},
    )

    assert arr.x.attrs == {}

    arrays.set_dim_attrs(
        arr,
        dim="x",
        units="m",
        long_name="Distance",
        standard_name="distance",
    )
    assert arr.x.attrs["units"] == "m"
    assert arr.x.attrs["long_name"] == "Distance"
    assert arr.x.attrs["standard_name"] == "distance"


def test_get_dim_width_is_succesful():
    """Test get_dim_width function."""
    arr = xr.DataArray(
        [1, 1, 1],
        dims=("x",),
        coords={"x": [0, 1, 2]},
    )
    assert arrays.get_dim_width(arr, "x") == 2


def test_get_dim_step_fails_if_exceeds_tolerance():
    """Test estimate_dim_step function."""
    arr = xr.DataArray(
        [1, 1, 1],
        dims=("x",),
        coords={"x": [0, 1, 4]},
    )

    with pytest.raises(ValueError):
        arrays.get_dim_step(arr, "x")

    assert arrays.get_dim_step(arr, "x", atol=1) == 2


def test_get_dim_fails_if_not_found_and_no_estimate():
    """Test estimate_dim_step function."""
    arr = xr.DataArray(
        [1, 1, 1],
        dims=("x",),
        coords={"x": [0, 1, 2]},
    )

    with pytest.raises(ValueError):
        arrays.get_dim_step(arr, "x", estimate_step=False)


def test_get_dim_step_estimates_step_if_not_found_in_attrs():
    """Test estimate_dim_step function."""
    arr = xr.DataArray(
        [1, 1, 1],
        dims=("x",),
        coords={"x": [0, 1, 2]},
    )

    assert arrays.get_dim_step(arr, "x") == 1


def test_get_dim_step_reads_step_from_attrs():
    """Test estimate_dim_step function."""
    arr = xr.DataArray(
        [1, 1, 1],
        dims=("x",),
        coords={"x": [0, 1, 2]},
    )
    arr.x.attrs["step"] = 0.5
    assert arrays.get_dim_step(arr, "x") == 0.5


def test_create_time_dim_from_array_sets_attrs():
    """Test create_time_dim_from_array function."""
    arr = np.array([1, 2, 3])
    time_dim = arrays.create_time_dim_from_array(arr)
    assert time_dim.attrs["units"] == "s"
    assert time_dim.attrs["long_name"] == "Time since start of recording"
    assert time_dim.attrs["standard_name"] == "time"


def test_create_time_dim_from_array_estimates_step():
    """Test create_time_dim_from_array function."""
    arr = np.array([1, 2, 3])
    time_dim = arrays.create_time_dim_from_array(arr, estimate_step=True)
    assert time_dim.attrs["step"] == 1


def test_can_give_step_to_create_time_dim_from_array():
    """Test create_time_dim_from_array function."""
    arr = np.array([1, 2, 3])
    time_dim = arrays.create_time_dim_from_array(arr, step=0.5)
    assert time_dim.attrs["step"] == 0.5


def test_can_give_samplerate_to_create_time_dim_from_array():
    """Test create_time_dim_from_array function."""
    arr = np.array([1, 2, 3])
    time_dim = arrays.create_time_dim_from_array(arr, samplerate=100)
    assert time_dim.attrs["step"] == 0.01


def test_create_frequency_dim_from_array_sets_attrs():
    """Test create_frequency_dim_from_array function."""
    arr = np.array([1, 2, 3])
    frequency_dim = arrays.create_frequency_dim_from_array(arr)
    assert frequency_dim.attrs["units"] == "Hz"
    assert frequency_dim.attrs["long_name"] == "Frequency"
    assert frequency_dim.attrs["standard_name"] == "frequency"


def test_create_frequency_dim_from_array_estimates_step():
    """Test create_frequency_dim_from_array function."""
    arr = np.array([1, 2, 3])
    frequency_dim = arrays.create_frequency_dim_from_array(
        arr, estimate_step=True
    )
    assert frequency_dim.attrs["step"] == 1


def test_can_give_step_to_create_frequency_dim_from_array():
    """Test create_frequency_dim_from_array function."""
    arr = np.array([1, 2, 3])
    frequency_dim = arrays.create_frequency_dim_from_array(arr, step=0.5)
    assert frequency_dim.attrs["step"] == 0.5


def test_create_range_dim_fails_without_step_and_size():
    """Test create_range_dim function."""
    with pytest.raises(ValueError):
        arrays.create_range_dim("x", start=0, stop=10)


def test_create_time_range_fail_if_no_step_or_samplerate():
    """Test create_time_dim function."""
    with pytest.raises(ValueError):
        arrays.create_time_range(start_time=0, end_time=10)
