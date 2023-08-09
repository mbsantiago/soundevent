"""Functions that handle SoundEvent geometries."""

import json

import shapely
from pydantic import ValidationError

from soundevent import data
from soundevent.data.geometries import GEOMETRY_MAPPING

__all__ = [
    "buffer_geometry",
    "geometry_validate",
]


def buffer_geometry(
    geometry: data.Geometry,
    time_buffer: data.Time = 0,
    freq_buffer: data.Frequency = 0,
    **kwargs,
) -> data.Geometry:
    """Buffer a geometry.

    Parameters
    ----------
    geometry : data.Geometry
        The geometry to buffer.

    time_buffer : float, optional
        The time buffer to apply to the geometry, in seconds.
        Defaults to 0.

    freq_buffer : float, optional
        The frequency buffer to apply to the geometry, in Hz.
        Defaults to 0.

    Returns
    -------
    geometry : data.Geometry
        The buffered geometry.
    """
    geom = geometry.geom
    factor = [
        1 / time_buffer if time_buffer > 0 else 1e9,
        1 / freq_buffer if freq_buffer > 0 else 1e9,
    ]
    transformed = shapely.transform(geom, lambda x: x * factor)
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


def geometry_validate(
    obj: object,
    mode: str = "json",
) -> data.Geometry:
    """Convert an object to a SoundEvent geometry.

    This function is particularly useful when loading a geometry from a
    different format, such as JSON or a dictionary. This function will
    convert the object to a SoundEvent geometry, and validate it.

    Parameters
    ----------
    obj : object
        The object to convert to a geometry.

    mode : str, optional
        Mode to use to convert the object to a geometry. Valid values are
        "json", "dict" and "attributes". If "json", the object is assumed
        to be a JSON string. If "dict", the object is assumed to be a
        dictionary. If "attributes", the object is assumed to be an object
        with attributes. Defaults to "json".

    Returns
    -------
    geometry : data.Geometry
        The geometry.

    Raises
    ------
    ValueError
        If the object is not a valid geometry.
    """
    if mode == "json":
        if not isinstance(obj, str):
            raise ValueError("Object must be a JSON string.")

        try:
            obj = json.loads(obj)
        except json.JSONDecodeError as error:
            raise ValueError("Object must be a valid JSON string.") from error
        mode = "dict"

    if mode == "dict":
        if not isinstance(obj, dict):
            raise ValueError("Object must be a dictionary.")

        if "type" not in obj:
            raise ValueError("Object must have a type key.")

        geom_type = obj["type"]
    else:
        if not hasattr(obj, "type"):
            raise ValueError(f"Object {obj} does not have a type attribute.")

        geom_type = getattr(obj, "type")

    if geom_type not in GEOMETRY_MAPPING:
        raise ValueError(f"Object {obj} does not have a geometry valid type.")

    geom_class = GEOMETRY_MAPPING[geom_type]

    try:
        return geom_class.model_validate(
            obj,
            from_attributes=mode == "attributes",
        )
    except ValidationError as error:
        raise ValueError(
            f"Object {obj} is not a valid {geom_type}."
        ) from error
