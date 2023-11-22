"""Functions that handle SoundEvent geometries."""

import json
from typing import Any, Tuple

import shapely

from soundevent import data
from soundevent.geometry.conversion import geometry_to_shapely

__all__ = [
    "buffer_geometry",
    "compute_bounds",
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
