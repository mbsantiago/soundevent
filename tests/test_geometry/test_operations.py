"""Test Suite for geometric operations."""

import math
from typing import List

import numpy as np
import pytest
import xarray as xr

from soundevent import arrays, data
from soundevent.data.geometries import BaseGeometry
from soundevent.geometry.operations import (
    buffer_geometry,
    compute_bounds,
    get_geometry_point,
    group_sound_events,
    have_frequency_overlap,
    have_temporal_overlap,
    is_in_clip,
    rasterize,
)


@pytest.fixture
def spec() -> xr.DataArray:
    """Create a DataArray with a time dimension."""
    return xr.DataArray(
        data=np.zeros((100, 100)),
        dims=["time", "frequency"],
        coords={
            "time": arrays.create_time_range(
                start_time=0,
                end_time=1,
                samplerate=100,
            ),
            "frequency": arrays.create_frequency_range(
                low_freq=0,
                high_freq=1000,
                step=10,
            ),
        },
    )


def test_compute_timestamp_bounds():
    """Test that compute_bounds works with TimeStamp geometries."""
    geom = data.TimeStamp(coordinates=2)
    bounds = compute_bounds(geom)
    assert bounds == (2, 0, 2, data.MAX_FREQUENCY)


def test_compute_timeinterval_bounds():
    """Test that compute_bounds works with TimeInterval geometries."""
    geom = data.TimeInterval(coordinates=[1, 2])
    bounds = compute_bounds(geom)
    assert bounds == (1, 0, 2, data.MAX_FREQUENCY)


def test_compute_bounding_box_bounds():
    """Test that compute_bounds works with BoundingBox geometries."""
    geom = data.BoundingBox(coordinates=[1, 2, 3, 4])
    bounds = compute_bounds(geom)
    assert bounds == (1, 2, 3, 4)


def test_compute_point_bounds():
    """Test that compute_bounds works with Point geometries."""
    geom = data.Point(coordinates=[1, 2])
    bounds = compute_bounds(geom)
    assert bounds == (1, 2, 1, 2)


def test_compute_linestring_bounds():
    """Test that compute_bounds works with LineString geometries."""
    geom = data.LineString(coordinates=[[1, 2], [3, 4]])
    bounds = compute_bounds(geom)
    assert bounds == (1, 2, 3, 4)


def test_compute_polygon_bounds():
    """Test that compute_bounds works with Polygon geometries."""
    geom = data.Polygon(coordinates=[[[1, 2], [3, 4], [5, 6], [1, 2]]])
    bounds = compute_bounds(geom)
    assert bounds == (1, 2, 5, 6)


def test_buffer_geometry_fails_with_non_positive_buffers():
    """Test that buffer_geometry fails with non-positive buffers."""
    with pytest.raises(ValueError):
        buffer_geometry(
            geometry=data.TimeInterval(coordinates=[0, 1]),
            time_buffer=-1,
        )

    with pytest.raises(ValueError):
        buffer_geometry(
            geometry=data.TimeInterval(coordinates=[0, 1]),
            freq_buffer=-1,
        )


def test_buffer_geometry_fails_with_unexpected_geometry():
    """Test that buffer_geometry fails with unexpected geometry."""

    class UnexpectedGeometry(BaseGeometry):
        coordinates: List[float]
        type: str = "unexpected"  # type: ignore

    geom = UnexpectedGeometry(coordinates=[0, 1])

    with pytest.raises(NotImplementedError):
        buffer_geometry(geometry=geom)  # type: ignore


def test_buffer_timestamp_geometry():
    """Test that buffer_geometry works with TimeStamp geometries."""
    geom = data.TimeStamp(coordinates=2)
    buffered_geom = buffer_geometry(geom, time_buffer=1)
    assert buffered_geom == data.TimeInterval(coordinates=[1, 3])


def test_buffer_timeinterval_geometry():
    """Test that buffer_geometry works with TimeInterval geometries."""
    geom = data.TimeInterval(coordinates=[1, 2])
    buffered_geom = buffer_geometry(geom, time_buffer=1)
    assert buffered_geom == data.TimeInterval(coordinates=[0, 3])


def test_buffer_boundingbox_geometry_in_freq_axis():
    """Test buffer_geometry works with BoundingBox in the frequency axis."""
    geom = data.BoundingBox(coordinates=[1, 2, 3, 4])
    buffered_geom = buffer_geometry(geom, freq_buffer=1)
    assert buffered_geom == data.BoundingBox(coordinates=[1, 1, 3, 5])


def test_buffer_boundingbox_geometry_in_time_axis():
    """Test buffer_geometry works with BoundingBox in the time axis."""
    geom = data.BoundingBox(coordinates=[1, 2, 3, 4])
    buffered_geom = buffer_geometry(geom, time_buffer=1)
    assert buffered_geom == data.BoundingBox(coordinates=[0, 2, 4, 4])


def test_buffered_geometry_time_is_not_negative():
    """Test that buffer_geometry fails when time buffer is negative."""
    geom = data.TimeInterval(coordinates=[1, 2])
    buffered = buffer_geometry(geom, time_buffer=2)
    assert buffered == data.TimeInterval(coordinates=[0, 4])


def test_buffered_geometry_freq_is_not_negative():
    """Test that buffer_geometry fails when frequency buffer is negative."""
    geom = data.BoundingBox(coordinates=[1, 2, 3, 4])
    buffered = buffer_geometry(geom, freq_buffer=2)
    assert buffered == data.BoundingBox(coordinates=[1, 0, 3, 6])


def test_buffer_polygon_geometry_in_time_axis():
    """Test that buffer_geometry works with Polygon geometries."""
    geom = data.Polygon(coordinates=[[[1, 2], [4, 3], [5, 6], [1, 2]]])
    buffered_geom = buffer_geometry(geom, time_buffer=1)
    bounds = compute_bounds(buffered_geom)
    assert math.isclose(bounds[0], 0, rel_tol=1e-6)
    assert math.isclose(bounds[1], 2, rel_tol=1e-6)
    assert math.isclose(bounds[2], 6, rel_tol=1e-6)
    assert math.isclose(bounds[3], 6, rel_tol=1e-6)


def test_buffer_polygon_geometry_in_freq_axis():
    """Test that buffer_geometry works with Polygon geometries."""
    geom = data.Polygon(coordinates=[[[1, 2], [4, 3], [5, 6], [1, 2]]])
    buffered_geom = buffer_geometry(geom, freq_buffer=1)
    bounds = compute_bounds(buffered_geom)
    assert math.isclose(bounds[0], 1, rel_tol=1e-6)
    assert math.isclose(bounds[1], 1, rel_tol=1e-6)
    assert math.isclose(bounds[2], 5, rel_tol=1e-6)
    assert math.isclose(bounds[3], 7, rel_tol=1e-6)


def test_rasterize_output_has_correct_shape(spec: xr.DataArray):
    """Test that rasterize_geometry produces a DataArray."""
    geom = data.TimeStamp(coordinates=0.5)
    mask = rasterize([geom], spec)
    assert isinstance(mask, xr.DataArray)
    assert mask.shape == spec.shape
    assert mask.dims == ("time", "frequency")
    assert (mask.coords["time"] == spec.coords["time"]).all()
    assert (mask.coords["frequency"] == spec.coords["frequency"]).all()


def test_rasterize_timestamp_geometry(
    spec: xr.DataArray,
):
    """Test that rasterize_geometry works with TimeStamp geometries."""
    time_stamp = data.TimeStamp(coordinates=0.5)
    mask = rasterize([time_stamp], spec)

    # Check that the mask is correct
    assert (mask.sel(time=0.5) == 1).all()
    assert (mask.sel(time=0.4) == 0).all()
    assert mask.sum() == spec.coords["frequency"].size


def test_rasterize_interval_geometry(
    spec: xr.DataArray,
):
    """Test that rasterize_geometry works with TimeInterval geometries."""
    time_interval = data.TimeInterval(coordinates=[0.4, 0.6])
    mask = rasterize([time_interval], spec)

    # Check that the mask is correct
    # NOTE: Rasterize is exclusive on the right side while DataArray.sel is
    # inclusive on both sides, hence the 0.59 instead of 0.6
    ones = mask.sel(time=slice(0.4, 0.59))
    assert ones.all()
    assert mask.sum() == ones.size


def test_rasterize_bbox_geometry(
    spec: xr.DataArray,
):
    """Test that rasterize_geometry works with BoundingBox geometries."""
    bbox = data.BoundingBox(coordinates=[0.4, 100, 0.6, 200])
    mask = rasterize([bbox], spec)

    # Check that the mask is correct
    # NOTE: Rasterize is exclusive on the right side while DataArray.sel is
    # inclusive on both sides, hence the 0.59 instead of 0.6
    ones = mask.sel(time=slice(0.4, 0.59), frequency=slice(100, 190))
    assert ones.all()
    assert mask.sum() == ones.size


def test_rasterize_linestring_geometry(
    spec: xr.DataArray,
):
    """Test that rasterize_geometry works with LineString geometries."""
    linestring = data.LineString(coordinates=[[0.4, 100], [0.6, 100]])
    mask = rasterize([linestring], spec)

    # Check that the mask is correct
    ones = mask.sel(time=slice(0.4, 0.6), frequency=100)
    assert ones.all()
    assert mask.sum() == ones.size


def test_rasterize_point_geometry(
    spec: xr.DataArray,
):
    """Test that rasterize_geometry works with Point geometries."""
    point = data.Point(coordinates=[0.5, 100])
    mask = rasterize([point], spec)

    # Check that the mask is correct
    ones = mask.sel(time=0.5, frequency=100)
    assert ones.all()
    assert mask.sum() == 1


def test_rasterize_with_multiple_geometries(spec: xr.DataArray):
    """Test that rasterize_geometry works with multiple geometries."""
    geom = [
        data.TimeStamp(coordinates=0.5),
        data.Point(coordinates=[0.7, 100]),
    ]
    mask = rasterize(geom, spec)

    # Check that the mask is correct
    assert (mask.sel(time=0.5) == 1).all()
    assert (mask.sel(time=0.7, frequency=100, method="ffill") == 1).all()


def test_rasterize_with_multiple_geometries_and_values(spec: xr.DataArray):
    """Test that rasterize_geometry works with multiple geometries and values."""
    geom = [
        data.TimeStamp(coordinates=0.5),
        data.Point(coordinates=[0.7, 100]),
    ]
    mask = rasterize(geom, spec, values=[3, 2])

    # Check that the mask is correct
    assert (mask.sel(time=0.5) == 3).all()
    assert (mask.sel(time=0.7, frequency=100, method="ffill") == 2).all()


def test_rasterize_fails_when_mismatching_values_and_geometries(
    spec: xr.DataArray,
):
    """Test that rasterize_geometry fails when values and geometries mismatch."""
    geom = [
        data.TimeStamp(coordinates=0.5),
        data.Point(coordinates=[0.7, 100]),
    ]
    with pytest.raises(ValueError):
        rasterize(geom, spec, values=[3, 2, 1])


def test_can_get_all_geometry_points_succesfully():
    # Triangle
    geom = data.Polygon(
        coordinates=[
            [
                [0, 0],
                [1, 1],
                [2, 0],
            ]
        ]
    )

    x, y = get_geometry_point(geom, position="bottom-left")
    assert x == 0
    assert y == 0

    x, y = get_geometry_point(geom, position="top-left")
    assert x == 0
    assert y == 1

    x, y = get_geometry_point(geom, position="top-right")
    assert x == 2
    assert y == 1

    x, y = get_geometry_point(geom, position="bottom-right")
    assert x == 2

    x, y = get_geometry_point(geom, position="center-left")
    assert x == 0
    assert y == 0.5

    x, y = get_geometry_point(geom, position="center-right")
    assert x == 2
    assert y == 0.5

    x, y = get_geometry_point(geom, position="top-center")
    assert x == 1
    assert y == 1

    x, y = get_geometry_point(geom, position="bottom-center")
    assert x == 1
    assert y == 0

    x, y = get_geometry_point(geom, position="center")
    assert x == 1
    assert y == 0.5

    x, y = get_geometry_point(geom, position="centroid")
    assert x == 1
    assert y == 0.3333333333333333

    x, y = get_geometry_point(geom, position="point_on_surface")
    assert x == 1
    assert y == 0.5


def test_get_geometry_point_fails_with_unexpected_position():
    """Test that get_geometry_point fails with unexpected position."""
    geom = data.Polygon(
        coordinates=[
            [
                [0, 0],
                [1, 1],
                [2, 0],
            ]
        ]
    )

    with pytest.raises(ValueError):
        get_geometry_point(geom, position="unexpected")  # type: ignore


def test_is_in_clip_fully_inside(recording: data.Recording):
    geometry = data.TimeInterval(coordinates=[1.0, 2.0])
    clip = data.Clip(start_time=0.0, end_time=5.0, recording=recording)
    assert is_in_clip(geometry, clip)


def test_is_in_clip_partially_inside(recording: data.Recording):
    geometry = data.TimeInterval(coordinates=[4.0, 6.0])
    clip = data.Clip(start_time=0.0, end_time=5.0, recording=recording)
    assert is_in_clip(geometry, clip)
    assert not is_in_clip(geometry, clip, minimum_overlap=1.0)
    assert is_in_clip(geometry, clip, minimum_overlap=0.5)


def test_is_in_clip_outside(recording: data.Recording):
    geometry = data.TimeInterval(coordinates=[6.0, 8.0])
    clip = data.Clip(start_time=0.0, end_time=5.0, recording=recording)
    assert not is_in_clip(geometry, clip)


def test_is_in_clip_edge_cases(recording: data.Recording):
    clip = data.Clip(start_time=1.0, end_time=5.0, recording=recording)

    geometry = data.TimeInterval(coordinates=[0.0, 1.0])
    assert not is_in_clip(geometry, clip)

    geometry = data.TimeInterval(coordinates=[5.0, 6.0])
    assert not is_in_clip(geometry, clip)


def test_is_in_clip_invalid_input(recording: data.Recording):
    geometry = data.TimeInterval(coordinates=[1.0, 3.0])
    clip = data.Clip(start_time=0.0, end_time=5.0, recording=recording)
    with pytest.raises(ValueError):
        is_in_clip(geometry, clip, minimum_overlap=-1.0)


def test_have_temporal_overlap_full_overlap():
    geom1 = data.TimeInterval(coordinates=[1.0, 3.0])
    geom2 = data.TimeInterval(coordinates=[0.0, 4.0])
    assert have_temporal_overlap(geom1, geom2)


def test_have_temporal_overlap_partial_overlap():
    geom1 = data.TimeInterval(coordinates=[1.0, 3.0])
    geom2 = data.TimeInterval(coordinates=[2.0, 4.0])
    assert have_temporal_overlap(geom1, geom2)
    assert have_temporal_overlap(geom1, geom2, min_absolute_overlap=0.5)
    assert not have_temporal_overlap(geom1, geom2, min_absolute_overlap=1.5)
    assert have_temporal_overlap(geom1, geom2, min_relative_overlap=0.25)
    assert not have_temporal_overlap(geom1, geom2, min_relative_overlap=0.75)


def test_have_temporal_overlap_no_overlap():
    geom1 = data.TimeInterval(coordinates=[1.0, 3.0])
    geom2 = data.TimeInterval(coordinates=[4.0, 5.0])
    assert not have_temporal_overlap(geom1, geom2)


def test_have_temporal_overlap_invalid_input():
    geom1 = data.TimeInterval(coordinates=[1.0, 3.0])
    geom2 = data.TimeInterval(coordinates=[2.0, 4.0])
    with pytest.raises(ValueError):
        have_temporal_overlap(
            geom1,
            geom2,
            min_absolute_overlap=1.0,
            min_relative_overlap=0.5,
        )
    with pytest.raises(ValueError):
        have_temporal_overlap(geom1, geom2, min_relative_overlap=-0.5)
    with pytest.raises(ValueError):
        have_temporal_overlap(geom1, geom2, min_relative_overlap=1.5)


def test_have_frequency_overlap_full_overlap():
    geom1 = data.BoundingBox(coordinates=[0, 100, 1, 200])
    geom2 = data.BoundingBox(coordinates=[2, 50, 3, 400])
    assert have_frequency_overlap(geom1, geom2)


def test_have_frequency_overlap_partial_overlap():
    geom1 = data.BoundingBox(coordinates=[0, 100, 1, 200])
    geom2 = data.BoundingBox(coordinates=[2, 150, 3, 250])
    assert have_frequency_overlap(geom1, geom2)
    assert have_frequency_overlap(geom1, geom2, min_absolute_overlap=25)
    assert not have_frequency_overlap(geom1, geom2, min_absolute_overlap=75)
    assert have_frequency_overlap(geom1, geom2, min_relative_overlap=0.25)
    assert not have_frequency_overlap(geom1, geom2, min_relative_overlap=0.75)


def test_have_frequency_overlap_no_overlap():
    geom1 = data.BoundingBox(coordinates=[0, 100, 1, 200])
    geom2 = data.BoundingBox(coordinates=[2, 300, 3, 400])
    assert not have_frequency_overlap(geom1, geom2)


def test_have_frequency_overlap_invalid_input():
    geom1 = data.BoundingBox(coordinates=[0, 100, 1, 200])
    geom2 = data.BoundingBox(coordinates=[2, 150, 3, 250])
    with pytest.raises(ValueError):
        have_frequency_overlap(
            geom1, geom2, min_absolute_overlap=50, min_relative_overlap=0.5
        )
    with pytest.raises(ValueError):
        have_frequency_overlap(geom1, geom2, min_relative_overlap=-0.5)
    with pytest.raises(ValueError):
        have_frequency_overlap(geom1, geom2, min_relative_overlap=1.5)


def test_group_sound_events_no_events():
    sound_events: list[data.SoundEvent] = []
    sequences = group_sound_events(sound_events, lambda se1, se2: se1 == se2)
    assert sequences == []


def test_group_sound_events_all_similar(recording: data.Recording):
    sound_events = [
        data.SoundEvent(
            recording=recording,
            geometry=data.TimeInterval(coordinates=[1, 2]),
        ),
        data.SoundEvent(
            recording=recording,
            geometry=data.TimeInterval(coordinates=[2, 3]),
        ),
        data.SoundEvent(
            recording=recording,
            geometry=data.TimeInterval(coordinates=[3, 4]),
        ),
    ]
    sequences = group_sound_events(sound_events, lambda se1, se2: True)
    assert len(sequences) == 1
    assert len(sequences[0].sound_events) == 3


def test_group_sound_events_no_similar(recording: data.Recording):
    sound_events = [
        data.SoundEvent(
            recording=recording,
            geometry=data.TimeInterval(coordinates=[1, 2]),
        ),
        data.SoundEvent(
            recording=recording,
            geometry=data.TimeInterval(coordinates=[2, 3]),
        ),
        data.SoundEvent(
            recording=recording,
            geometry=data.TimeInterval(coordinates=[3, 4]),
        ),
    ]
    sequences = group_sound_events(sound_events, lambda se1, se2: False)
    assert len(sequences) == 3
    for sequence in sequences:
        assert len(sequence.sound_events) == 1


def test_group_sound_events_some_similar(recording: data.Recording):
    sound_events = [
        data.SoundEvent(
            recording=recording,
            geometry=data.TimeInterval(coordinates=[1, 2]),
        ),
        data.SoundEvent(
            recording=recording,
            geometry=data.TimeInterval(coordinates=[3, 4]),
        ),
        data.SoundEvent(
            recording=recording,
            geometry=data.TimeInterval(coordinates=[3, 5]),
        ),
    ]

    def comparison_fn(se1: data.SoundEvent, se2: data.SoundEvent):
        if se1.geometry is None or se2.geometry is None:
            return False
        return have_temporal_overlap(se1.geometry, se2.geometry)

    sequences = group_sound_events(sound_events, comparison_fn)
    assert len(sequences) == 2
    assert any(
        len(sequence.sound_events) == 2 for sequence in sequences
    )  # Group of 2 similar events
    assert any(
        len(sequence.sound_events) == 1 for sequence in sequences
    )  # The remaining event


def test_group_sound_events_transitive_similarity(recording: data.Recording):
    sound_events = [
        data.SoundEvent(
            recording=recording,
            geometry=data.TimeInterval(coordinates=[1, 3]),
        ),
        data.SoundEvent(
            recording=recording,
            geometry=data.TimeInterval(coordinates=[2, 5]),
        ),
        data.SoundEvent(
            recording=recording,
            geometry=data.TimeInterval(coordinates=[4, 6]),
        ),
    ]

    def comparison_fn(se1: data.SoundEvent, se2: data.SoundEvent):
        if se1.geometry is None or se2.geometry is None:
            return False
        return have_temporal_overlap(se1.geometry, se2.geometry)

    sequences = group_sound_events(sound_events, comparison_fn)
    assert len(sequences) == 1
    assert len(sequences[0].sound_events) == 3  # All in the same group
