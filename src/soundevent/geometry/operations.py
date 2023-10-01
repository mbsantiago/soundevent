"""Functions that handle SoundEvent geometries."""

import json

import shapely

from soundevent import data

__all__ = [
    "buffer_geometry",
]


def buffer_geometry(
    geometry: shapely.Geometry,
    time_buffer: data.Time = 0,
    freq_buffer: data.Frequency = 0,
    **kwargs,
) -> data.Geometry:
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
    return data.Polygon(coordinates=json_data["coordinates"])
