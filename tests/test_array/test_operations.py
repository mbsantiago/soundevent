"""Test suite for the soundevent.arrays.operations module."""

import numpy as np
import pytest
import xarray as xr

from soundevent.arrays import operations as ops


def test_successful_cropping():
    """Test successful cropping of an axis."""
    data = xr.DataArray(range(10), dims=["x"], coords={"x": range(10)})
    result = ops.crop_dim(data, "x", 2, 7)

    # Check dimensions and values
    assert result.dims == ("x",)
    assert result.x.values.tolist() == [2, 3, 4, 5, 6]


def test_closed_interval_cropping():
    """Test successful extending of an axis."""
    data = xr.DataArray(range(10), dims=["x"], coords={"x": range(10)})
    result = ops.crop_dim(data, "x", 2, 7, right_closed=True)

    # Check dimensions and values
    assert result.dims == ("x",)
    assert result.x.values.tolist() == [2, 3, 4, 5, 6, 7]


def test_left_open_interval_cropping():
    """Test successful extending of an axis."""
    data = xr.DataArray(range(10), dims=["x"], coords={"x": range(10)})
    result = ops.crop_dim(data, "x", 2, 7, left_closed=False)

    # Check dimensions and values
    assert result.dims == ("x",)
    assert result.x.values.tolist() == [3, 4, 5, 6]


def test_crop_fails_if_start_is_greater_than_end():
    """Test that cropping fails if the start index is greater than the end index."""
    data = xr.DataArray(range(10), dims=["x"], coords={"x": range(10)})

    with pytest.raises(ValueError):
        ops.crop_dim(data, "x", 7, 2)


def test_crop_fails_if_trying_to_crop_outside_of_bounds():
    """Test that cropping fails if the start index is greater than the end index."""
    data = xr.DataArray(range(10), dims=["x"], coords={"x": range(10)})

    with pytest.raises(ValueError):
        ops.crop_dim(data, "x", -1, 11)


def test_crop_without_start():
    """Test that cropping an axis without a start index works."""
    data = xr.DataArray(range(10), dims=["x"], coords={"x": range(10)})
    result = ops.crop_dim(data, "x", stop=7)

    # Check dimensions and values
    assert result.dims == ("x",)
    assert result.x.values.tolist() == [0, 1, 2, 3, 4, 5, 6]


def test_crop_without_end():
    """Test that cropping an axis without an end index works."""
    data = xr.DataArray(range(10), dims=["x"], coords={"x": range(10)})
    result = ops.crop_dim(data, "x", start=2)

    # Check dimensions and values
    assert result.dims == ("x",)
    assert result.x.values.tolist() == [2, 3, 4, 5, 6, 7, 8, 9]


def test_successful_extension():
    """Test successful extending of an axis."""
    data = xr.DataArray(range(10), dims=["x"], coords={"x": range(10)})
    result = ops.extend_dim(data, "x", start=-1, stop=11)

    # Check dimensions and values
    assert result.dims == ("x",)
    assert result.x.values.tolist() == [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def test_extend_fails_if_start_is_greater_than_end():
    """Test that extending fails if the start index is greater than the end index."""
    data = xr.DataArray(range(10), dims=["x"], coords={"x": range(10)})

    with pytest.raises(ValueError):
        ops.extend_dim(data, "x", start=7, stop=2)


def test_extend_left_open_interval():
    """Test successful extending of an axis with a left-open interval."""
    data = xr.DataArray(range(5), dims=["x"], coords={"x": range(5)})
    result = ops.extend_dim(data, "x", start=-2, left_closed=False)

    # Check dimensions and values
    assert result.dims == ("x",)
    assert result.x.values.tolist() == [-1, 0, 1, 2, 3, 4]


def test_extend_right_closed():
    """Test successful extending of an axis with a right-closed interval."""
    data = xr.DataArray(range(5), dims=["x"], coords={"x": range(5)})
    result = ops.extend_dim(data, "x", stop=7, right_closed=True)

    # Check dimensions and values
    assert result.dims == ("x",)
    assert result.x.values.tolist() == [0, 1, 2, 3, 4, 5, 6, 7]


def test_extend_non_exact_range():
    """Test successful extending of an axis with a non-exact range."""
    data = xr.DataArray(range(5), dims=["x"], coords={"x": range(5)})
    result = ops.extend_dim(data, "x", start=-2.5, stop=7.5)

    # Check dimensions and values
    assert result.dims == ("x",)
    assert result.x.values.tolist() == [-2, -1, 0, 1, 2, 3, 4, 5, 6, 7]


def test_set_value_at_exact_position():
    """Test setting a value at an exact position."""
    data = xr.DataArray(np.zeros(5), dims=["x"], coords={"x": range(5)})
    result = ops.set_value_at_pos(data, 1, x=0)
    assert result.values.tolist() == [1, 0, 0, 0, 0]

    data = xr.DataArray(np.zeros(5), dims=["x"], coords={"x": range(5)})
    result = ops.set_value_at_pos(data, 1, x=1)
    assert result.values.tolist() == [0, 1, 0, 0, 0]

    data = xr.DataArray(np.zeros(5), dims=["x"], coords={"x": range(5)})
    result = ops.set_value_at_pos(data, 1, x=2)
    assert result.values.tolist() == [0, 0, 1, 0, 0]

    data = xr.DataArray(np.zeros(5), dims=["x"], coords={"x": range(5)})
    result = ops.set_value_at_pos(data, 1, x=3)
    assert result.values.tolist() == [0, 0, 0, 1, 0]

    data = xr.DataArray(np.zeros(5), dims=["x"], coords={"x": range(5)})
    result = ops.set_value_at_pos(data, 1, x=4)
    assert result.values.tolist() == [0, 0, 0, 0, 1]


def test_set_value_at_non_exact_position():
    """Test setting a value at a non-exact position."""
    data = xr.DataArray(np.zeros(5), dims=["x"], coords={"x": range(5)})
    result = ops.set_value_at_pos(data, 1, x=0.5)
    assert result.values.tolist() == [1, 0, 0, 0, 0]

    data = xr.DataArray(np.zeros(5), dims=["x"], coords={"x": range(5)})
    result = ops.set_value_at_pos(data, 1, x=0.9)
    assert result.values.tolist() == [1, 0, 0, 0, 0]

    data = xr.DataArray(np.zeros(5), dims=["x"], coords={"x": range(5)})
    result = ops.set_value_at_pos(data, 1, x=1.1)
    assert result.values.tolist() == [0, 1, 0, 0, 0]


def test_set_value_in_2d_array():
    """Test setting a value at a position in a 2D array."""
    data = xr.DataArray(
        np.zeros((3, 3)),
        dims=["x", "y"],
        coords={"x": range(3), "y": range(3)},
    )
    result = ops.set_value_at_pos(data, 1, x=1, y=1)
    assert result.values.tolist() == [[0, 0, 0], [0, 1, 0], [0, 0, 0]]


def test_set_value_at_position_outside_of_bounds():
    """Test that setting a value at a position outside of the bounds of the axis raises an error."""
    data = xr.DataArray(np.zeros(5), dims=["x"], coords={"x": range(5)})

    with pytest.raises(KeyError):
        ops.set_value_at_pos(data, 1, x=-1)

    with pytest.raises(KeyError):
        ops.set_value_at_pos(data, 1, x=6)


def test_set_array_value_at_position():
    """Test setting an array value at a position."""
    data = xr.DataArray(
        np.zeros((3, 3)),
        dims=["x", "y"],
        coords={"x": range(3), "y": range(3)},
    )
    value = np.array([1, 2, 3])
    result = ops.set_value_at_pos(data, value, x=1)
    assert result.values.tolist() == [[0, 0, 0], [1, 2, 3], [0, 0, 0]]


def test_set_tuple_at_position():
    """Test setting a tuple value at a position."""
    data = xr.DataArray(
        np.zeros((3, 3)),
        dims=["x", "y"],
        coords={"x": range(3), "y": range(3)},
    )
    value = (1, 2, 3)
    result = ops.set_value_at_pos(data, value, x=1)
    assert result.values.tolist() == [[0, 0, 0], [1, 2, 3], [0, 0, 0]]


def test_set_variable_value_at_position():
    """Test setting a variable value at a position."""
    data = xr.DataArray(
        np.zeros((3, 3, 3)),
        dims=["x", "y", "z"],
        coords={"x": range(3), "y": range(3), "z": range(3)},
    )
    value = xr.DataArray(
        np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
        dims=["y", "z"],
        coords={"y": range(3), "z": range(3)},
    )
    result = ops.set_value_at_pos(data, value, x=1)
    assert result.values.tolist() == [
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
    ]


def test_set_variable_value_at_position_fails_with_invalid_dimension():
    """Test that setting a variable value at a position fails with an invalid dimension."""
    data = xr.DataArray(
        np.zeros((3, 3, 3)),
        dims=["x", "y", "z"],
        coords={"x": range(3), "y": range(3), "z": range(3)},
    )

    with pytest.raises(ValueError):
        ops.set_value_at_pos(data, 1, w=1)


def test_offset_attribute_is_stored():
    """Test that the offset attribute is stored in the output."""
    data = xr.DataArray(range(5), dims=["x"], coords={"x": range(5)})
    result = ops.offset(data, 1)
    assert result.attrs["add_offset"] == -1
    assert result.values.tolist() == [1, 2, 3, 4, 5]


def test_scale_attribute_is_stored():
    """Test that the scale attribute is stored in the output."""
    data = xr.DataArray(range(5), dims=["x"], coords={"x": range(5)})
    result = ops.scale(data, 2)
    assert result.attrs["scale_factor"] == 0.5
    assert result.values.tolist() == [0, 2, 4, 6, 8]


def test_normalize_has_correct_range():
    """Test that the output of normalize has the correct range."""
    data = xr.DataArray(range(5), dims=["x"], coords={"x": range(5)})
    result = ops.normalize(data)
    assert result.values.tolist() == [0, 0.25, 0.5, 0.75, 1]


def test_normalize_stores_offset_and_scale_attributes():
    """Test that the output of normalize has the correct attributes."""
    data = xr.DataArray(
        data=np.array([1, 2, 3, 4, 5]),
        dims=["x"],
        coords={"x": range(5)},
    )
    result = ops.normalize(data)
    assert result.attrs["add_offset"] == 1
    assert result.attrs["scale_factor"] == 4


def test_normalize_a_constant_array():
    """Test that normalize works with a constant array."""
    data = xr.DataArray(np.ones(5), dims=["x"], coords={"x": range(5)})
    result = ops.normalize(data)
    assert result.values.tolist() == [0, 0, 0, 0, 0]


def test_center_removes_mean():
    """Test that the output of center has a mean of zero."""
    data = xr.DataArray(range(5), dims=["x"], coords={"x": range(5)})
    result = ops.center(data)
    assert result.values.mean() == 0


def test_center_stores_offset_attribute():
    """Test that the output of center has the correct offset attribute."""
    data = xr.DataArray(range(5), dims=["x"], coords={"x": range(5)})
    result = ops.center(data)
    assert result.attrs["add_offset"] == 2.0


def test_resize_has_correct_shape():
    """Test that the output of resize has the correct shape."""
    data = xr.DataArray(
        data=np.array([[1, 2], [3, 4]]),
        dims=["x", "y"],
        coords={"x": range(2), "y": range(2)},
    )
    result = ops.resize(data, x=3, y=3)
    assert result.shape == (3, 3)


def test_resize_has_correct_coordinates():
    """Test that the output of resize has the correct dimension."""
    data = xr.DataArray(
        data=np.array([[1, 2], [3, 4]]),
        dims=["x", "y"],
        coords={"x": range(2), "y": range(2)},
    )
    result = ops.resize(data, x=3, y=3)
    assert result.x.values.tolist() == [0, 2 / 3, 4 / 3]
    assert result.y.values.tolist() == [0, 2 / 3, 4 / 3]


def test_resize_fails_if_dimension_name_is_invalid():
    """Test that resize fails if the dimension name is invalid."""
    data = xr.DataArray(
        data=np.array([[1, 2], [3, 4]]),
        dims=["x", "y"],
        coords={"x": range(2), "y": range(2)},
    )

    with pytest.raises(ValueError):
        ops.resize(data, z=3)


def test_resize_with_subset_of_dimensions():
    """Test that resize works with a subset of dimensions."""
    data = xr.DataArray(
        data=np.array([[1, 2], [3, 4]]),
        dims=["x", "y"],
        coords={"x": range(2), "y": range(2)},
    )
    result = ops.resize(data, x=3)
    assert result.shape == (3, 2)


def test_to_db_with_power_values():
    """Test that to_db returns the correct values."""
    data = xr.DataArray(
        data=np.array([0.001, 0.01, 0.1, 1, 10, 100, 1000]),
        dims=["x"],
        coords={"x": range(7)},
    )
    result = ops.to_db(data)
    assert result.values.tolist() == [-30, -20, -10, 0, 10, 20, 30]


def test_to_db_with_amplitude_values():
    """Test that to_db returns the correct values for amplitude values."""
    data = xr.DataArray(
        data=np.array([0.001, 0.01, 0.1, 1, 10, 100, 1000]),
        dims=["x"],
        coords={"x": range(7)},
    )
    result = ops.to_db(data, power=2)
    assert result.values.tolist() == [-60, -40, -20, 0, 20, 40, 60]


def test_to_db_with_max_reference():
    """Test that to_db returns the correct values with a reference value."""
    data = xr.DataArray(
        data=np.array([0.001, 0.01, 0.1, 1, 10, 100, 1000]),
        dims=["x"],
        coords={"x": range(7)},
    )
    result = ops.to_db(data, ref=np.max)
    assert result.values.tolist() == [-60, -50, -40, -30, -20, -10, 0]


def test_to_db_with_min_db():
    """Test that to_db returns the correct values with a minimum value."""
    data = xr.DataArray(
        data=np.array([0.001, 0.01, 0.1, 1, 10, 100, 1000]),
        dims=["x"],
        coords={"x": range(7)},
    )
    result = ops.to_db(data, ref=np.max, min_db=-40)
    assert result.values.tolist() == [-40, -40, -40, -30, -20, -10, 0]


def test_to_db_with_max_db():
    """Test that to_db returns the correct values with a maximum value."""
    data = xr.DataArray(
        data=np.array([0.001, 0.01, 0.1, 1, 10, 100, 1000]),
        dims=["x"],
        coords={"x": range(7)},
    )
    result = ops.to_db(data, ref=np.max, max_db=-20)
    assert result.values.tolist() == [-60, -50, -40, -30, -20, -20, -20]


def test_to_db_adjust_unit_attribute():
    """Test that to_db adjusts the unit attribute."""
    data = xr.DataArray(
        data=np.array([0.001, 0.01, 0.1, 1, 10, 100, 1000]),
        dims=["x"],
        coords={"x": range(7)},
        attrs={"units": "V"},
    )
    result = ops.to_db(data)
    assert result.attrs["units"] == "V dB"


def test_to_db_adds_db_unit():
    """Test that to_db adds the correct unit if it is not present."""
    data = xr.DataArray(
        data=np.array([0.001, 0.01, 0.1, 1, 10, 100, 1000]),
        dims=["x"],
        coords={"x": range(7)},
    )
    result = ops.to_db(data)
    assert result.attrs["units"] == "dB"


def test_to_db_has_sane_values_for_zero_values():
    """Test that to_db returns sane values for zero values."""
    data = xr.DataArray(
        data=np.array([0, 0, 0, 0, 0]),
        dims=["x"],
        coords={"x": range(5)},
    )
    result = ops.to_db(data)
    assert result.values.tolist() == [-80, -80, -80, -80, -80]


def test_to_db_validates_arguments():
    """Test that to_db validates its arguments."""
    data = xr.DataArray(
        data=np.array([0.001, 0.01, 0.1, 1, 10, 100, 1000]),
        dims=["x"],
        coords={"x": range(7)},
    )

    with pytest.raises(ValueError):
        ops.to_db(data, amin=-1)

    with pytest.raises(ValueError):
        ops.to_db(data, ref=-1)


def test_adjust_dim_range_raises_if_no_start_or_stop():
    array = xr.DataArray(
        np.arange(10), dims=["x"], coords={"x": np.arange(10)}
    )
    with pytest.raises(ValueError):
        ops.adjust_dim_range(array, dim="x")


def test_adjust_dim_range_crop_start():
    array = xr.DataArray(
        np.arange(10),
        dims=["x"],
        coords={"x": np.arange(10)},
    )
    result = ops.adjust_dim_range(array, dim="x", start=2.5)
    expected = xr.DataArray(
        np.arange(2, 10),
        dims=["x"],
        coords={"x": np.arange(2, 10)},
    )
    xr.testing.assert_identical(result, expected)


def test_adjust_dim_range_crop_stop():
    array = xr.DataArray(
        np.arange(10),
        dims=["x"],
        coords={"x": np.arange(10)},
    )
    result = ops.adjust_dim_range(array, dim="x", stop=7.5)
    expected = xr.DataArray(
        np.arange(8),
        dims=["x"],
        coords={"x": np.arange(8)},
    )
    xr.testing.assert_equal(result, expected)


def test_adjust_dim_range_extend_start():
    array = xr.DataArray(
        np.arange(10), dims=["x"], coords={"x": np.arange(10)}
    )
    result = ops.adjust_dim_range(array, dim="x", start=-2.5, fill_value=-1)
    expected = xr.DataArray(
        np.concatenate([[-1, -1, -1], np.arange(10)]),
        dims=["x"],
        coords={"x": np.arange(-3, 10)},
    )
    xr.testing.assert_equal(result, expected)


def test_adjust_dim_range_extend_stop():
    array = xr.DataArray(
        np.arange(10), dims=["x"], coords={"x": np.arange(10)}
    )
    result = ops.adjust_dim_range(array, dim="x", stop=12.5, fill_value=-1)
    expected = xr.DataArray(
        np.concatenate([np.arange(10), [-1, -1, -1]]),
        dims=["x"],
        coords={"x": np.arange(13)},
    )
    xr.testing.assert_equal(result, expected)


def test_adjust_dim_range_both_start_stop():
    array = xr.DataArray(
        np.arange(10), dims=["x"], coords={"x": np.arange(10)}
    )
    result = ops.adjust_dim_range(array, dim="x", start=2.5, stop=7.5)
    expected = xr.DataArray(
        np.arange(2, 8), dims=["x"], coords={"x": np.arange(2, 8)}
    )
    xr.testing.assert_equal(result, expected)


def test_adjust_dim_range_with_non_exact_range():
    array = xr.DataArray(
        np.arange(10),
        dims=["x"],
        coords={"x": np.linspace(0, 1, 10, endpoint=False)},
    )
    result = ops.adjust_dim_range(array, dim="x", start=0.35, stop=0.67)
    expected = xr.DataArray(
        np.array([3, 4, 5, 6]),
        dims=["x"],
        coords={"x": np.array([0.3, 0.4, 0.5, 0.6])},
    )
    xr.testing.assert_allclose(result, expected)


def test_adjust_dim_range_invalid_input():
    array = xr.DataArray(
        np.arange(10), dims=["x"], coords={"x": np.arange(10)}
    )
    with pytest.raises(ValueError):
        ops.adjust_dim_range(array, dim="x", start=5.0, stop=2.0)
    with pytest.raises(ValueError):
        ops.adjust_dim_range(array, dim="x", start=None, stop=None)


def test_adjust_dim_width_when_width_is_shorter():
    array = xr.DataArray(
        np.arange(10),
        dims=["x"],
        coords={"x": np.arange(10)},
    )

    result = ops.adjust_dim_width(array, dim="x", width=5, position="start")
    expected = xr.DataArray(
        np.arange(5), dims=["x"], coords={"x": np.arange(5)}
    )
    xr.testing.assert_equal(result, expected)

    result = ops.adjust_dim_width(array, dim="x", width=5, position="center")
    expected = xr.DataArray(
        np.arange(3, 8), dims=["x"], coords={"x": np.arange(3, 8)}
    )
    xr.testing.assert_equal(result, expected)

    result = ops.adjust_dim_width(array, dim="x", width=5, position="end")
    expected = xr.DataArray(
        np.arange(5, 10), dims=["x"], coords={"x": np.arange(5, 10)}
    )
    xr.testing.assert_equal(result, expected)


def test_adjust_dim_with_is_a_noop_when_width_is_same():
    array = xr.DataArray(
        np.arange(10),
        dims=["x"],
        coords={"x": np.arange(10)},
    )
    result = ops.adjust_dim_width(array, dim="x", width=10, position="start")
    xr.testing.assert_equal(result, array)
    result = ops.adjust_dim_width(array, dim="x", width=10, position="center")
    xr.testing.assert_equal(result, array)
    result = ops.adjust_dim_width(array, dim="x", width=10, position="end")
    xr.testing.assert_equal(result, array)


def test_adjust_dim_width_fails_if_position_is_invalid():
    array = xr.DataArray(
        np.arange(10),
        dims=["x"],
        coords={"x": np.arange(10)},
    )

    with pytest.raises(ValueError):
        ops.adjust_dim_width(array, dim="x", width=5, position="top")  # type: ignore


def test_adjust_dim_width_when_width_is_longer():
    array = xr.DataArray(
        np.arange(10),
        dims=["x"],
        coords={"x": np.arange(10)},
    )
    result = ops.adjust_dim_width(array, dim="x", width=15, position="start")
    expected = xr.DataArray(
        np.concatenate([np.arange(10), np.zeros(5)]),
        dims=["x"],
        coords={"x": np.arange(0, 15)},
    )
    xr.testing.assert_equal(result, expected)

    result = ops.adjust_dim_width(array, dim="x", width=15, position="center")
    expected = xr.DataArray(
        np.concatenate([np.zeros(2), np.arange(10), np.zeros(3)]),
        dims=["x"],
        coords={"x": np.arange(-2, 13)},
    )
    xr.testing.assert_equal(result, expected)

    result = ops.adjust_dim_width(array, dim="x", width=15, position="end")
    expected = xr.DataArray(
        np.concatenate([np.zeros(5), np.arange(10)]),
        dims=["x"],
        coords={"x": np.arange(-5, 10)},
    )
    xr.testing.assert_equal(result, expected)


def test_that_extend_dim_width_fails_if_width_is_less_than_current():
    array = xr.DataArray(
        np.arange(10),
        dims=["x"],
        coords={"x": np.arange(10)},
    )
    with pytest.raises(ValueError):
        ops.extend_dim_width(array, dim="x", width=2)


def test_that_crop_dim_width_fails_if_width_is_larger_than_current():
    array = xr.DataArray(
        np.arange(10),
        dims=["x"],
        coords={"x": np.arange(10)},
    )
    with pytest.raises(ValueError):
        ops.crop_dim_width(array, dim="x", width=20)


def test_extend_dim_width_fails_if_position_is_invalid():
    array = xr.DataArray(
        np.arange(10),
        dims=["x"],
        coords={"x": np.arange(10)},
    )
    with pytest.raises(ValueError):
        ops.extend_dim_width(array, dim="x", width=15, position="top")  # type: ignore


def test_that_crop_dim_width_fails_if_position_is_invalid():
    array = xr.DataArray(
        np.arange(10),
        dims=["x"],
        coords={"x": np.arange(10)},
    )
    with pytest.raises(ValueError):
        ops.crop_dim_width(array, dim="x", width=5, position="top")  # type: ignore


def test_adjust_dim_width_fails_if_width_is_too_short():
    array = xr.DataArray(
        np.arange(10),
        dims=["x"],
        coords={"x": np.arange(10)},
    )
    with pytest.raises(ValueError):
        ops.adjust_dim_width(array, dim="x", width=0, position="start")
