"""Functions that handle SoundEvent geometries."""

import json
from collections import defaultdict
from itertools import combinations
from typing import (
    Any,
    Callable,
    List,
    Literal,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import numpy as np
import shapely
import xarray as xr
from numpy.typing import DTypeLike
from rasterio import features
from scipy import sparse
from scipy.sparse.csgraph import connected_components

from soundevent import data
from soundevent.arrays import (
    Dimensions,
    get_coord_index,
)
from soundevent.data import Geometry
from soundevent.geometry.conversion import geometry_to_shapely

__all__ = [
    "buffer_geometry",
    "compute_bounds",
    "get_geometry_point",
    "group_sound_events",
    "have_frequency_overlap",
    "have_temporal_overlap",
    "intervals_overlap",
    "is_in_clip",
    "rasterize",
]


def compute_bounds(
    geometry: data.Geometry,
) -> Tuple[float, float, float, float]:
    """Compute the bounds of a geometry.

    Parameters
    ----------
    geometry
        The geometry to compute the bounds of.

    Returns
    -------
    bounds : tuple[float, float, float, float]
        The bounds of the geometry. The bounds are returned in the
        following order: start_time, low_freq, end_time, high_freq.
    """
    shp_geom = geometry_to_shapely(geometry)
    return shp_geom.bounds


def buffer_timestamp(
    geometry: data.TimeStamp,
    time_buffer: data.Time = 0,
) -> data.TimeInterval:
    """Buffer a TimeStamp geometry.

    Parameters
    ----------
    geometry
        The geometry to buffer.
    time_buffer
        The time buffer to apply to the geometry, in seconds.
        Defaults to 0.

    Returns
    -------
    geometry : data.TimeInterval
        The buffered geometry.
    """
    time = geometry.coordinates
    start_time = max(time - time_buffer, 0)
    end_time = time + time_buffer
    return data.TimeInterval(coordinates=[start_time, end_time])


def buffer_interval(
    geometry: data.TimeInterval,
    time_buffer: data.Time = 0,
) -> data.TimeInterval:
    """Buffer a TimeInterval geometry.

    Parameters
    ----------
    geometry
        The geometry to buffer.
    time_buffer
        The time buffer to apply to the geometry, in seconds.
        Defaults to 0.

    Returns
    -------
    geometry : data.TimeInterval
        The buffered geometry.
    """
    start_time, end_time = geometry.coordinates
    start_time = max(start_time - time_buffer, 0)
    end_time += time_buffer
    return data.TimeInterval(coordinates=[start_time, end_time])


def buffer_bounding_box_geometry(
    geometry: data.BoundingBox,
    time_buffer: data.Time = 0,
    freq_buffer: data.Frequency = 0,
) -> data.BoundingBox:
    """Buffer a BoundingBox geometry.

    Parameters
    ----------
    geometry
        The geometry to buffer.
    time_buffer
        The time buffer to apply to the geometry, in seconds.
        Defaults to 0.
    freq_buffer
        The frequency buffer to apply to the geometry, in Hz.
        Defaults to 0.

    Returns
    -------
    geometry : data.BoundingBox
        The buffered geometry.
    """
    start_time, low_freq, end_time, high_freq = geometry.coordinates
    start_time = max(start_time - time_buffer, 0)
    low_freq = max(low_freq - freq_buffer, 0)
    end_time += time_buffer
    high_freq = min(high_freq + freq_buffer, data.MAX_FREQUENCY)
    return data.BoundingBox(
        coordinates=[start_time, low_freq, end_time, high_freq],
    )


def buffer_geometry(
    geometry: data.Geometry,
    time_buffer: data.Time = 0,
    freq_buffer: data.Frequency = 0,
    **kwargs: Any,
):
    """Buffer a geometry.

    Parameters
    ----------
    geometry
        The geometry to buffer.
    time_buffer
        The time buffer to apply to the geometry, in seconds.
        Defaults to 0.
    freq_buffer
        The frequency buffer to apply to the geometry, in Hz.
        Defaults to 0.
    **kwargs
        Additional keyword arguments to pass to the Shapely buffer
        function.

    Returns
    -------
    geometry : data.Geometry
        The buffered geometry.

    Raises
    ------
    NotImplementedError
        If the geometry type is not supported.
    ValueError
        If the time buffer or the frequency buffer is negative.
    """
    if time_buffer < 0 or freq_buffer < 0:
        raise ValueError(
            "The time buffer and the frequency buffer must be non negative."
        )

    if geometry.type == "TimeStamp":
        return buffer_timestamp(geometry, time_buffer=time_buffer)
    if geometry.type == "TimeInterval":
        return buffer_interval(geometry, time_buffer=time_buffer)
    if geometry.type == "BoundingBox":
        return buffer_bounding_box_geometry(
            geometry,
            time_buffer=time_buffer,
            freq_buffer=freq_buffer,
        )

    shp_geom = geometry_to_shapely(geometry)
    return buffer_shapely_geometry(
        shp_geom,
        time_buffer=time_buffer,
        freq_buffer=freq_buffer,
        **kwargs,
    )


def buffer_shapely_geometry(
    geometry: shapely.Geometry,
    time_buffer: data.Time = 0,
    freq_buffer: data.Frequency = 0,
    **kwargs,
) -> data.Geometry:
    """Buffer a shapely geometry.

    Parameters
    ----------
    geometry
        The geometry to buffer.
    time_buffer
        The time buffer to apply to the geometry, in seconds.
        Defaults to 0.
    freq_buffer
        The frequency buffer to apply to the geometry, in Hz.
        Defaults to 0.

    Returns
    -------
    geometry : data.Geometry
        The buffered geometry.
    """
    factor = [
        1 / time_buffer if time_buffer > 0 else 1e9,
        1 / freq_buffer if freq_buffer > 0 else 1e9,
    ]
    transformed = shapely.transform(geometry, lambda x: x * factor)
    buffered = shapely.buffer(
        transformed,
        1,
        cap_style="round",
        join_style="mitre",
        **kwargs,
    )
    buffered = shapely.transform(buffered, lambda x: x / factor)
    max_time = buffered.bounds[2]
    buffered = shapely.clip_by_rect(
        buffered,
        0,
        0,
        max_time + 1,
        data.MAX_FREQUENCY,
    )
    json_data = json.loads(shapely.to_geojson(buffered))
    if json_data["type"] == "Polygon":
        return data.Polygon(coordinates=json_data["coordinates"])
    return data.MultiPolygon(coordinates=json_data["coordinates"])


Value = Union[float, int]


def rasterize(
    geometries: List[data.Geometry],
    array: xr.DataArray,
    values: Union[Value, List[Value], Tuple[Value]] = 1,
    fill: float = 0,
    dtype: DTypeLike = np.float32,
    xdim: str = Dimensions.time.value,
    ydim: str = Dimensions.frequency.value,
    all_touched: bool = False,
) -> xr.DataArray:
    """Rasterize geometric objects into an xarray DataArray.

    This function takes a list of geometric objects (`geometries`) and
    rasterizes them into a specified `xr.DataArray`. Each geometry can be
    associated with a `value`, which is used to fill the corresponding pixels
    in the rasterized array.

    Parameters
    ----------
    geometries
        A list of `Geometry` objects to rasterize.
    array
        The xarray DataArray into which the geometries will be rasterized.
    values
        The values to fill the rasterized pixels for each geometry. If a single
        value is provided, it will be used for all geometries. If a list or
        tuple of values is provided, it must have the same length as the
        `geometries` list. Defaults to 1.
    fill
        The value to fill pixels not covered by any geometry. Defaults to 0.
    dtype
        The data type of the output rasterized array. Defaults to np.float32.
    xdim
        The name of the dimension representing the x-axis in the DataArray.
        Defaults to "time".
    ydim
        The name of the dimension representing the y-axis in the DataArray.
        Defaults to "frequency".
    all_touched
        If True, all pixels touched by geometries will be filled, otherwise
        only pixels whose center point is within the geometry are filled.
        Defaults to False.

    Returns
    -------
    xr.DataArray
        A new xarray DataArray containing the rasterized data, with the same
        coordinates and dimensions as the input `array`.

    Raises
    ------
    ValueError
        If the number of `values` does not match the number of `geometries`.
    """
    if not isinstance(values, (list, tuple)):
        values = [values] * len(geometries)

    if len(values) != len(geometries):
        raise ValueError(
            "The number of values must match the number of geometries."
        )

    def transform_coordinates(coords: np.ndarray):
        return np.array(
            [
                [
                    get_coord_index(array, xdim, x, raise_error=False),
                    get_coord_index(array, ydim, y, raise_error=False),
                ]
                for x, y in coords
            ],
            dtype=np.float64,
        )

    shapely_geometries = [
        shapely.transform(geometry_to_shapely(geom), transform_coordinates)
        for geom in geometries
    ]

    rast = features.rasterize(
        [(geom, val) for geom, val in zip(shapely_geometries, values)],
        array.shape,
        default_value=1,
        dtype=dtype,
        fill=fill,  # type: ignore
        all_touched=all_touched,
    )

    return xr.DataArray(
        data=rast.T,
        dims=(xdim, ydim),
        coords={
            xdim: array.coords[xdim],
            ydim: array.coords[ydim],
        },
    )


Positions = Literal[
    "bottom-left",
    "bottom-right",
    "top-left",
    "top-right",
    "center-left",
    "center-right",
    "top-center",
    "bottom-center",
    "center",
    "centroid",
    "point_on_surface",
]


def get_geometry_point(
    geometry: Geometry,
    position: Positions = "bottom-left",
) -> Tuple[float, float]:
    """
    Calculate the coordinates of a specific point within a geometry.

    Parameters
    ----------
    geometry
        The geometry object for which to calculate the point coordinates.
    position
        The specific point within the geometry to calculate coordinates for.
        Defaults to 'bottom-left'.

    Returns
    -------
    Tuple[float, float]
        The coordinates of the specified point within the geometry.

    Raises
    ------
    ValueError
        If an invalid point is specified.

    Notes
    -----
    The following positions are supported:

    - 'bottom-left': The point defined by the start time and lowest frequency
        of the geometry.
    - 'bottom-right': The point defined by the end time and lowest frequency
        of the geometry.
    - 'top-left': The point defined by the start time and highest frequency
        of the geometry.
    - 'top-right': The point defined by the end time and highest frequency
        of the geometry.
    - 'center-left': The point defined by the middle time and lowest frequency
        of the geometry.
    - 'center-right': The point defined by the middle time and highest frequency
        of the geometry.
    - 'top-center': The point defined by the end time and middle frequency
        of the geometry.
    - 'bottom-center': The point defined by the start time and middle frequency
        of the geometry.
    - 'center': The point defined by the middle time and middle frequency
        of the geometry.
    - 'centroid': The centroid of the geometry. Computed using the shapely
        library.
    - 'point_on_surface': A point on the surface of the geometry. Computed
        using the shapely library.

    For all positions except 'centroid' and 'point_on_surface', the time and
    frequency values are calculated by first computing the bounds of the
    geometry and then determining the appropriate values based on the
    specified point type.
    """
    if position not in [
        "bottom-left",
        "bottom-right",
        "top-left",
        "top-right",
        "center-left",
        "center-right",
        "top-center",
        "bottom-center",
        "center",
        "centroid",
        "point_on_surface",
    ]:
        raise ValueError(f"Invalid point type: {position}")

    if position == "centroid":
        shp_geom = geometry_to_shapely(geometry)
        return shp_geom.centroid.coords[0]

    if position == "point_on_surface":
        shp_geom = geometry_to_shapely(geometry)
        return shapely.point_on_surface(shp_geom).coords[0]

    start_time, low_freq, end_time, high_freq = compute_bounds(geometry)

    if position == "center":
        return (start_time + end_time) / 2, (low_freq + high_freq) / 2

    y, x = position.split("-")

    time_pos = {
        "left": start_time,
        "center": (start_time + end_time) / 2,
        "right": end_time,
    }[x]

    freq_pos = {
        "bottom": low_freq,
        "center": (low_freq + high_freq) / 2,
        "top": high_freq,
    }[y]

    return time_pos, freq_pos


def is_in_clip(
    geometry: data.Geometry,
    clip: data.Clip,
    minimum_overlap: float = 0,
) -> bool:
    """Check if a geometry lies within a clip, considering a minimum overlap.

    This function determines whether a given geometry falls within the
    time boundaries of a clip. It takes into account a `minimum_overlap`
    parameter, which specifies the minimum required temporal overlap
    (in seconds) between the geometry and the clip for the geometry to be
    considered inside the clip.

    Parameters
    ----------
    geometry
        The geometry object to be checked.
    clip
        The clip object to check against.
    minimum_overlap
        The minimum required overlap between the geometry and the clip
        in seconds. Defaults to 0, meaning any overlap is sufficient.

    Returns
    -------
    bool
        True if the geometry is within the clip with the specified
        minimum overlap, False otherwise.

    Raises
    ------
    ValueError
        If the `minimum_overlap` is negative.

    Examples
    --------
    >>> from soundevent import data
    >>> geometry = data.Geometry(...)
    >>> clip = data.Clip(start_time=0.0, end_time=5.0, ...)
    >>> is_in_clip(geometry, clip, minimum_overlap=0.5)
    True
    """
    if minimum_overlap < 0:
        raise ValueError("The minimum overlap must be non-negative.")

    start_time, _, end_time, _ = compute_bounds(geometry)

    if (end_time <= clip.start_time + minimum_overlap) or (
        start_time >= clip.end_time - minimum_overlap
    ):
        return False

    return True


def intervals_overlap(
    interval1: tuple[float, float],
    interval2: tuple[float, float],
    min_absolute_overlap: Optional[float] = None,
    min_relative_overlap: Optional[float] = None,
):
    """Check if two intervals overlap.

    This function determines whether two intervals, represented as tuples of
    (start, stop) values, have any overlap. It optionally allows specifying a
    minimum required overlap, either in absolute terms or relative to the
    smaller interval.

    Parameters
    ----------
    interval1 : tuple[float, float]
        The first interval, as a tuple (start, stop).
    interval2 : tuple[float, float]
        The second interval, as a tuple (start, stop).
    min_absolute_overlap : float, optional
        The minimum required absolute overlap. Defaults to None, meaning
        any overlap is sufficient.
    min_relative_overlap : float, optional
        The minimum required relative overlap (between 0 and 1). Defaults
        to None.

    Returns
    -------
    bool
        True if the intervals overlap with the specified minimum overlap,
        False otherwise.

    Raises
    ------
    ValueError
        - If both `min_absolute_overlap` and `min_relative_overlap` are
        provided.
        - If `min_relative_overlap` is not in the range [0, 1].

    Examples
    --------
    >>> intervals_overlap((1.0, 3.0), (2.0, 4.0))
    True
    >>> intervals_overlap(
    ...     (1.0, 3.0),
    ...     (2.0, 4.0),
    ...     min_absolute_overlap=0.5,
    ... )
    True
    >>> intervals_overlap(
    ...     (1.0, 3.0),
    ...     (2.0, 4.0),
    ...     min_absolute_overlap=1.5,
    ... )
    False
    >>> intervals_overlap(
    ...     (1.0, 3.0),
    ...     (2.0, 4.0),
    ...     min_relative_overlap=0.25,
    ... )
    True
    >>> intervals_overlap(
    ...     (1.0, 3.0),
    ...     (2.0, 4.0),
    ...     min_relative_overlap=0.75,
    ... )
    False
    """
    if min_absolute_overlap is not None and min_relative_overlap is not None:
        raise ValueError(
            "Only one of min_absolute_overlap or "
            "min_relative_overlap can be provided."
        )

    start1, stop1 = interval1
    start2, stop2 = interval2
    start = max(start1, start2)
    stop = min(stop1, stop2)

    overlap = 0
    if min_absolute_overlap is not None:
        overlap = min_absolute_overlap

    if min_relative_overlap is not None:
        if min_relative_overlap < 0 or min_relative_overlap > 1:
            raise ValueError("The minimum relative overlap must be in [0, 1].")

        min_width = min(
            stop1 - start1,
            stop2 - start2,
        )
        overlap = min_relative_overlap * min_width

    return stop - start >= overlap


def have_temporal_overlap(
    geom1: data.Geometry,
    geom2: data.Geometry,
    min_absolute_overlap: Optional[float] = None,
    min_relative_overlap: Optional[float] = None,
) -> bool:
    """Check if two geometries have temporal overlap.

    This function determines whether two geometry objects have any time
    overlap, optionally considering a minimum required overlap, either in
    absolute terms (seconds) or relative to the shorter duration of the
    two geometries.

    Parameters
    ----------
    geom1 : data.Geometry
        The first geometry object.
    geom2 : data.Geometry
        The second geometry object.
    min_absolute_overlap : float, optional
        The minimum required absolute overlap in seconds. Defaults to None,
        meaning any overlap is sufficient.
    min_relative_overlap : float, optional
        The minimum required relative overlap (between 0 and 1). Defaults
        to None.

    Returns
    -------
    bool
        True if the geometries overlap with the specified minimum overlap,
        False otherwise.

    Raises
    ------
    ValueError
        - If both `min_absolute_overlap` and `min_relative_overlap` are
        provided.
        - If `min_relative_overlap` is not in the range [0, 1].
    """
    start_time_1, _, end_time_1, _ = compute_bounds(geom1)
    start_time_2, _, end_time_2, _ = compute_bounds(geom2)
    return intervals_overlap(
        (start_time_1, end_time_1),
        (start_time_2, end_time_2),
        min_absolute_overlap=min_absolute_overlap,
        min_relative_overlap=min_relative_overlap,
    )


def have_frequency_overlap(
    geom1: data.Geometry,
    geom2: data.Geometry,
    min_absolute_overlap: Optional[float] = None,
    min_relative_overlap: Optional[float] = None,
) -> bool:
    """Check if two geometries have frequency overlap.

    This function determines whether two geometry objects have any frequency
    overlap, optionally considering a minimum required overlap, either in
    absolute terms (Hz) or relative to the smaller frequency range of the
    two geometries.

    Parameters
    ----------
    geom1 : data.Geometry
        The first geometry object.
    geom2 : data.Geometry
        The second geometry object.
    min_absolute_overlap : float, optional
        The minimum required absolute overlap in Hz. Defaults to None,
        meaning any overlap is sufficient.
    min_relative_overlap : float, optional
        The minimum required relative overlap (between 0 and 1). Defaults
        to None.

    Returns
    -------
    bool
        True if the geometries overlap with the specified minimum overlap,
        False otherwise.

    Raises
    ------
    ValueError
        - If both `min_absolute_overlap` and `min_relative_overlap` are
        provided.
        - If `min_relative_overlap` is not in the range [0, 1].
    """
    _, low_freq_1, _, high_freq_1 = compute_bounds(geom1)
    _, low_freq_2, _, high_freq_2 = compute_bounds(geom2)
    return intervals_overlap(
        (low_freq_1, high_freq_1),
        (low_freq_2, high_freq_2),
        min_absolute_overlap=min_absolute_overlap,
        min_relative_overlap=min_relative_overlap,
    )


def group_sound_events(
    sound_events: Sequence[data.SoundEvent],
    comparison_fn: Callable[[data.SoundEvent, data.SoundEvent], bool],
) -> list[data.Sequence]:
    """Group sound events into sequences based on a pairwise comparison.

    This function takes a sequence of `data.SoundEvent` objects and a
    comparison function. It applies the comparison function to all pairs
    of sound events to determine their similarity. Sound events that are
    deemed similar are grouped together into `data.Sequence` objects.

    The comparison function should take two `data.SoundEvent` objects as
    input and return True if they are considered similar, and False
    otherwise.

    Parameters
    ----------
    sound_events : Sequence[data.SoundEvent]
        A sequence of `data.SoundEvent` objects to be grouped.
    comparison_fn : Callable[[data.SoundEvent, data.SoundEvent], bool]
        A function that compares two `data.SoundEvent` objects and
        returns True if they should be grouped together, False otherwise.

    Returns
    -------
    list[data.Sequence]
        A list of `data.Sequence` objects, where each sequence contains
        a group of similar sound events.

    Notes
    -----
    This function groups sound events based on **transitive similarity**. While
    it uses pairwise comparisons, the final groups (sequences) can include
    sound events that aren't directly similar according to your
    `comparison_fn`. Think of it like a chain:  sound event A is similar to B,
    B is similar to C, but A might not be similar to C directly. They all end
    up in the same group because of their connections through B. Technically,
    this works by finding the connected components in a graph where the sound
    events are nodes, and the edges represent similarity based on your
    `comparison_fn`.

    Examples
    --------
    >>> # Define a comparison function based on temporal overlap
    >>> def compare_sound_events(se1, se2):
    ...     return have_temporal_overlap(
    ...         se1.geometry, se2.geometry, min_absolute_overlap=0.5
    ...     )
    >>> # Group sound events with the comparison function
    >>> sequences = group_sound_events(
    ...     sound_events, compare_sound_events
    ... )
    """
    similarity_matrix = _compute_similarity_matrix(
        sound_events,
        comparison_fn,
    )
    _, labels = connected_components(similarity_matrix)

    sequences = defaultdict(data.Sequence)
    for sound_event, label in zip(sound_events, labels):
        sequence = sequences[label]
        sequence.sound_events.append(sound_event)

    return list(sequences.values())


def _compute_similarity_matrix(
    sound_events: Sequence[data.SoundEvent],
    comparison_fn: Callable[[data.SoundEvent, data.SoundEvent], bool],
) -> sparse.coo_array:
    """Compute the similarity matrix for sound events.

    This helper function generates a sparse similarity matrix
    representing the pairwise similarity between sound events based on
    the provided comparison function.
    """
    col = []
    row = []
    values = []
    for (index1, se1), (index2, se2) in combinations(
        enumerate(sound_events), 2
    ):
        if not comparison_fn(se1, se2):
            continue

        col.extend([index1, index2])
        row.extend([index2, index1])
        values.extend([1, 1])

    rows = len(sound_events)
    return sparse.coo_array(
        (values, (col, row)),
        shape=(rows, rows),
        dtype=np.int8,
    )
