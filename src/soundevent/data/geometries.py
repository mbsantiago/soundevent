"""Geometry types.

Sound event geometry plays a crucial role in locating and describing
sound events within a recording. Different geometry types offer
flexibility in representing the location of sound events, allowing for
varying levels of detail and precision. The soundevent package follows
the GeoJSON specification for geometry types and provides support for
a range of geometry types.

## Units and Time Reference

All geometries in the soundevent package utilize seconds as the unit
for time and hertz as the unit for frequency. It is important to note
that time values are always relative to the start of the recording. By
consistently using these units, it becomes easier to develop functions
and interact with geometry objects based on convenient assumptions.

## Supported Geometry Types

The soundevent package supports the following geometry types, each
serving a specific purpose in describing the location of sound events:

* TimeStamp: Represents a single point in time.

* TimeInterval: Describes a time interval, indicating a range of time
within which the sound event occurs.

* Point: Represents a specific point in time and frequency,
pinpointing the exact location of the sound event.

* LineString: Represents a sequence of points in time and frequency,
allowing for the description of continuous sound events.

* Polygon: Defines a closed shape in time and frequency, enabling the
representation of complex sound event regions.

* Box: Represents a rectangle in time and frequency, useful for
specifying rectangular sound event areas.

* Multi-Point: Describes a collection of points, allowing for the
representation of multiple sound events occurring at different
locations.

* Multi-Line String: Represents a collection of line strings, useful
for capturing multiple continuous sound events.

* Multi-Polygon: Defines a collection of polygons, accommodating
complex and overlapping sound event regions.

By offering these geometry types, the soundevent package provides a
comprehensive framework for accurately and flexibly describing the
location and extent of sound events within a recording.
"""

import json
from abc import ABC
from typing import Dict, List, Literal, Type, Union

from pydantic import BaseModel, Field, ValidationError, field_validator

__all__ = [
    "BoundingBox",
    "Frequency",
    "Geometry",
    "GeometryType",
    "LineString",
    "MAX_FREQUENCY",
    "MultiLineString",
    "MultiPoint",
    "MultiPolygon",
    "Point",
    "Polygon",
    "Time",
    "TimeInterval",
    "TimeStamp",
    "geometry_validate",
]

TimeStampName = Literal["TimeStamp"]
TimeIntervalName = Literal["TimeInterval"]
BoundingBoxName = Literal["BoundingBox"]
PointName = Literal["Point"]
LineStringName = Literal["LineString"]
PolygonName = Literal["Polygon"]
MultiPointName = Literal["MultiPoint"]
MultiLineStringName = Literal["MultiLineString"]
MultiPolygonName = Literal["MultiPolygon"]

GeometryType = Union[
    TimeStampName,
    TimeIntervalName,
    BoundingBoxName,
    PointName,
    LineStringName,
    PolygonName,
    MultiPointName,
    MultiLineStringName,
    MultiPolygonName,
]

Time = float
"""Time in seconds."""

Frequency = float
"""Frequency in Hertz."""

MAX_FREQUENCY = 5_000_000
"""The absolute maximum frequency that can be used in a geometry."""


class BaseGeometry(BaseModel, ABC):
    """Base Geometry Class.

    The `BaseGeometry` class serves as the foundation for various geometrical
    representations used in sound event localization. It provides a consistent
    structure for handling geometric objects and ensures synchronization with
    Shapely geometry objects. Instances of classes derived from `BaseGeometry`
    represent different types of spatial entities and facilitate accurate
    localization of sound events within audio data.

    Attributes
    ----------
    type
        The type of geometry used to locate the sound event. This attribute is
        essential for categorizing and identifying the specific geometric
        representation employed, such as points, polygons, or circles.
    coordinates
        The coordinates of the geometry. Depending on the geometry type, this
        attribute can represent a single pair of coordinates (for points) or a
        list of coordinate pairs (for polygons or other multi-point geometries).
        Properly structured coordinates are crucial for accurately defining the
        spatial extent of the geometry.

    Notes
    -----
        Mutation of geometry objects is not allowed. This restriction ensures
        that the geometry object remains immutable and always in sync with the
        underlying Shapely geometry object. Immutable geometries enhance
        reliability and consistency in spatial calculations.
    """

    @classmethod
    def geom_type(cls) -> GeometryType:
        """Get the geometry type.

        Returns
        -------
        str
            The Shapely geometry type.
        """
        type_field = cls.model_fields["type"]
        return type_field.default

    def _repr_html_(self) -> str:
        try:
            from soundevent.geometry import geometry_to_html

            return geometry_to_html(self)  # type: ignore
        except ImportError:
            return repr(self)


class TimeStamp(BaseGeometry):
    """TimeStamp Geometry Class.

    The `TimeStamp` class represents a specific time point within an audio
    recording where a sound event occurs. This geometry type is particularly
    useful for very short sound events that are not well-represented by a time
    interval. `TimeStamp` provides precise temporal localization, indicating
    the exact moment when a sound event is detected.

    Attributes
    ----------
    type
        The type of geometry, always set to "TimeStamp," indicating the
        specific geometry type being utilized. This attribute ensures clear
        identification of the geometry representation and its intended purpose.
    coordinates
        The time stamp of the sound event, specifying the exact moment, in
        seconds, when the event occurred relative to the start of the
        recording. The time stamp is represented in a standard format, allowing
        for consistent interpretation and synchronization across different
        applications and systems.
    """

    type: TimeStampName = "TimeStamp"

    coordinates: Time = Field(
        ...,
        description="The time stamp of the sound event.",
    )

    @field_validator("coordinates")
    def _positive_times(cls, v: Time) -> Time:
        """Validate that the time is positive."""
        if v < 0:
            raise ValueError("The time must be positive.")
        return v


class TimeInterval(BaseGeometry):
    """TimeInterval Geometry Class.

    The `TimeInterval` class represents a specific time interval within an audio
    recording where a sound event occurs. This geometry type is particularly useful
    for events that have a clear start and end time but lack a well-defined frequency
    range. `TimeInterval` provides a structured way to define the duration of such
    sound events, allowing for accurate temporal localization.

    Attributes
    ----------
    type
        The type of geometry, always set to "TimeInterval," indicating the specific
        geometry type being utilized. This attribute ensures clear identification
        of the geometry representation and its intended purpose.
    coordinates
        The time interval of the sound event, specifying the start and end times
        of the event relative to the start of the recording. The time interval is
        represented as a list of two `Time` objects, indicating the beginning and
        end of the event. This structured format enables precise definition of the
        event's duration.
    """

    type: TimeIntervalName = "TimeInterval"

    coordinates: List[Time] = Field(
        description="The time interval of the sound event.",
    )

    @field_validator("coordinates")
    def _validate_time_interval(cls, v: List[Time]) -> List[Time]:
        """Validate that the time interval is valid.

        Parameters
        ----------
        v : List[Time]
            The time interval to validate.

        Returns
        -------
            The validated time interval.

        Raises
        ------
            ValueError: If the time interval is invalid (i.e. the start time is
                after the end time).
        """
        if len(v) != 2:
            raise ValueError(
                "The time interval must have exactly two time stamps."
            )

        if v[0] > v[1]:
            raise ValueError("The start time must be before the end time.")
        return v

    @field_validator("coordinates")
    def _positive_times(cls, v: List[Time]) -> List[Time]:
        """Validate that the times are positive."""
        if any(time < 0 for time in v):
            raise ValueError("The times must be positive.")
        return v


class Point(BaseGeometry):
    """Point Geometry Class.

    The `Point` class represents a specific point in time and frequency within an
    audio recording where a sound event occurs. This geometry type provides precise
    localization, indicating both the exact moment and frequency content of the
    event. `Point` is ideal for events with well-defined temporal and spectral
    characteristics, enabling accurate pinpointing of sound occurrences.

    Attributes
    ----------
    type
        The type of geometry, always set to "Point," indicating the specific
        geometry type being utilized. This attribute ensures clear identification
        of the geometry representation and its intended purpose.
    coordinates
        The points of the sound event, specifying both the time and frequency
        components of the event relative to the start of the recording. The
        `coordinates` attribute is represented as a list of two float values,
        indicating the time and frequency of the event. This structured format
        enables accurate localization of the sound event within the recording.
    """

    type: PointName = "Point"

    coordinates: List[float] = Field(
        ...,
        description="The points of the sound event.",
    )

    @field_validator("coordinates")
    def _validate_coordinates(cls, v: List[float]) -> List[float]:
        """Validate that the coordinates are valid.

        Parameters
        ----------
        v : List[float]
            The coordinates to validate.

        Returns
        -------
            The validated coordinates.

        Raises
        ------
            ValueError: If the coordinates are invalid (i.e. the time is
                negative or the frequency is outside the valid range).
        """
        if len(v) != 2:
            raise ValueError("The coordinates must have exactly two values.")

        time, frequency = v

        if time < 0:
            raise ValueError("The time must be positive.")

        if frequency < 0 or frequency > MAX_FREQUENCY:
            raise ValueError(
                f"The frequency must be between 0 and {MAX_FREQUENCY}."
            )

        return v


class LineString(BaseGeometry):
    """LineString Geometry Class.

    The `LineString` class represents a continuous trajectory of sound events
    within an audio recording, defined by a sequence of points in both time and
    frequency. This geometry type is particularly valuable for events with
    clear and defined frequency trajectories, allowing for detailed mapping of
    sound occurrences over time. `LineString` provides a comprehensive
    representation for events that exhibit specific frequency patterns or
    modulations.

    Attributes
    ----------
    type
        The type of geometry, always set to "LineString," indicating the
        specific geometry type being utilized. This attribute ensures clear
        identification of the geometry representation and its intended purpose.
    coordinates
        The line of the sound event, specifying the trajectory of the event as
        a list of points in both time and frequency. Each point is represented
        as a list of two float values, indicating the time and frequency
        coordinates of the event. The `coordinates` attribute is ordered by
        time, providing a clear sequence of the sound event's trajectory within
        the recording.
    """

    type: LineStringName = "LineString"

    coordinates: List[List[float]] = Field(
        ...,
        description="The line of the sound event.",
    )

    @field_validator("coordinates")
    def _validate_coordinates(cls, v: List[List[float]]) -> List[List[float]]:
        """Validate that the coordinates are valid.

        Parameters
        ----------
        v : List[List[float]]
            The coordinates to validate.

        Returns
        -------
            The validated coordinates.

        Raises
        ------
            ValueError: If the coordinates are invalid (i.e. the time is
                negative or the frequency is outside the valid range).
        """
        if len(v) < 2:
            raise ValueError("The line must have at least two points.")

        for time, frequency in v:
            if time < 0:
                raise ValueError("The time must be positive.")

            if frequency < 0 or frequency > MAX_FREQUENCY:
                raise ValueError(
                    f"The frequency must be between 0 and {MAX_FREQUENCY}."
                )

        return v

    @field_validator("coordinates")
    def _is_ordered_by_time(cls, v: List[List[float]]) -> List[List[float]]:
        """Validate that the line is ordered by time."""
        start_time = v[0][0]
        end_time = v[-1][0]
        if start_time > end_time:
            return v[::-1]
        return v


class Polygon(BaseGeometry):
    """Polygon Geometry Class.

    The `Polygon` class represents complex-shaped sound events within an audio
    recording, defined by a polygonal boundary in both time and frequency. This
    geometry type is valuable for events that do not exhibit a concentrated
    frequency band and are contained within intricate shapes on the
    spectrogram. `Polygon` provides a detailed and accurate representation for
    sound events that require precise spatial localization and have diverse
    frequency distributions.

    Attributes
    ----------
    type
        The type of geometry, always set to "Polygon," indicating the specific
        geometry type being utilized. This attribute ensures clear
        identification of the geometry representation and its intended purpose.
    coordinates
        The polygon of the sound event, specifying the boundary of the event as
        a list of points in both time and frequency. Each point is represented
        as a list of two float values, indicating the time and frequency
        coordinates of the event. The `coordinates` attribute represents the
        polygonal shape of the sound event, allowing for detailed mapping of
        its extent within the recording.
    """

    type: PolygonName = "Polygon"

    coordinates: List[List[List[float]]] = Field(
        ...,
        description="The polygon of the sound event.",
    )

    @field_validator("coordinates")
    def _validate_coordinates(
        cls, v: List[List[List[float]]]
    ) -> List[List[List[float]]]:
        """Validate that the coordinates are valid.

        Parameters
        ----------
        v : List[List[List[float]]]
            The coordinates to validate.

        Returns
        -------
            The validated coordinates.

        Raises
        ------
            ValueError: If the coordinates are invalid (i.e. the time is
                negative or the frequency is outside the valid range).
        """
        if len(v) < 1:
            raise ValueError("The polygon must have at least one ring.")

        for ring in v:
            if len(ring) < 3:
                raise ValueError("The ring must have at least three points.")

            for time, frequency in ring:
                if time < 0:
                    raise ValueError("The time must be positive.")

                if frequency < 0 or frequency > MAX_FREQUENCY:
                    raise ValueError(
                        f"The frequency must be between 0 and "
                        f"{MAX_FREQUENCY}."
                    )

        return v


class BoundingBox(BaseGeometry):
    """Bounding Box Geometry Class.

    The `BoundingBox` class represents sound events within an audio recording,
    defined by a rectangular bounding box in both time and frequency. This
    geometry type is suitable for events with clear and well-defined frequency
    ranges, start and stop times. `BoundingBox` provides a simple yet effective
    way to localize sound events within a specific time interval and frequency
    band, enabling accurate mapping of events that exhibit distinct spectral
    content.

    Attributes
    ----------
    type
        The type of geometry, always set to "BoundingBox," indicating the
        specific geometry type being utilized. This attribute ensures clear
        identification of the geometry representation and its intended purpose.
    coordinates
        The bounding box of the sound event, specifying the start and end times
        as well as the start and end frequencies of the event. The
        `coordinates` attribute is represented as a list of four float values
        in the format (start time, start frequency, end time, end frequency).
        All times are relative to the start of the recording. This format
        allows precise localization of the event within the recording.
    """

    type: BoundingBoxName = "BoundingBox"

    coordinates: List[float] = Field(
        ...,
        description="The bounding box of the sound event.",
    )

    @field_validator("coordinates")
    def _validate_coordinates(cls, v: List[float]) -> List[float]:
        """Validate that the coordinates are valid.

        Parameters
        ----------
        v : List[float]
            The coordinates to validate.

        Returns
        -------
            The validated coordinates.

        Raises
        ------
            ValueError: If the coordinates are invalid (i.e. the time is
                negative or the frequency is outside the valid range).
        """
        if len(v) != 4:
            raise ValueError(
                "The bounding box must have exactly four coordinates."
            )

        start_time, low_freq, end_time, high_freq = v

        if start_time < 0:
            raise ValueError("The start time must be positive.")

        if low_freq < 0 or low_freq > MAX_FREQUENCY:
            raise ValueError(
                f"The start frequency must be between 0 and {MAX_FREQUENCY}."
            )

        if end_time < 0:
            raise ValueError("The end time must be positive.")

        if high_freq < 0 or high_freq > MAX_FREQUENCY:
            raise ValueError(
                f"The end frequency must be between 0 and {MAX_FREQUENCY}."
            )

        if start_time > end_time:
            start_time, end_time = end_time, start_time

        if low_freq > high_freq:
            low_freq, high_freq = high_freq, low_freq

        return [start_time, low_freq, end_time, high_freq]


class MultiPoint(BaseGeometry):
    """MultiPoint Geometry Class.

    The `MultiPoint` class represents sound events within an audio recording,
    defined by multiple points in both time and frequency. This geometry type
    is suitable for events that consist of multiple interesting points
    distributed across the spectrogram. `MultiPoint` allows researchers to
    identify and map several distinct points within an event, providing a
    detailed representation for complex acoustic patterns.

    Attributes
    ----------
    type
        The type of geometry, always set to "MultiPoint," indicating the
        specific geometry type being utilized. This attribute ensures clear
        identification of the geometry representation and its intended purpose.
    coordinates
        The points of the sound event, specifying the time and frequency
        coordinates of each interesting point within the event. The
        `coordinates` attribute is represented as a list of lists, where each
        inner list contains two float values representing the time and
        frequency of a point. All times are relative to the start of the
        recording. This format allows for the localization of multiple points
        within the recording.
    """

    type: MultiPointName = "MultiPoint"

    coordinates: List[List[float]] = Field(
        ...,
        description="The points of the sound event.",
    )

    @field_validator("coordinates")
    def _validate_coordinates(cls, v: List[List[float]]) -> List[List[float]]:
        """Validate that the coordinates are valid.

        Parameters
        ----------
        v : List[List[float]]
            The coordinates to validate.

        Returns
        -------
            The validated coordinates.

        Raises
        ------
            ValueError: If the coordinates are invalid (i.e. the time is
                negative or the frequency is outside the valid range).
        """
        if len(v) < 1:
            raise ValueError("The multipoint must have at least one point.")

        for time, frequency in v:
            if time < 0:
                raise ValueError("The time must be positive.")

            if frequency < 0 or frequency > MAX_FREQUENCY:
                raise ValueError(
                    f"The frequency must be between 0 and {MAX_FREQUENCY}."
                )

        return v


class MultiLineString(BaseGeometry):
    """MultiLineString Geometry Class.

    The `MultiLineString` class represents sound events within an audio
    recording, defined by multiple lines in both time and frequency. This
    geometry type is suitable for events that consist of multiple interesting
    lines distributed across the spectrogram. `MultiLineString` allows
    researchers to identify and map several distinct lines within an event,
    providing a detailed representation for complex acoustic patterns, such as
    events with multiple harmonics.

    Attributes
    ----------
    type
        The type of geometry, always set to "MultiLineString," indicating the
        specific geometry type being utilized. This attribute ensures clear
        identification of the geometry representation and its intended purpose.
    coordinates
        The lines of the sound event, specifying the time and frequency
        coordinates of each point in each line within the event. The
        `coordinates` attribute is represented as a list of lists of lists,
        where each innermost list contains two float values representing the
        time and frequency of a point. All times are relative to the start of
        the recording. This format allows for the localization of multiple
        lines within the recording.
    """

    type: MultiLineStringName = "MultiLineString"

    coordinates: List[List[List[float]]] = Field(
        ...,
        description="The lines of the sound event.",
    )

    @field_validator("coordinates")
    def _validate_coordinates(
        cls, v: List[List[List[float]]]
    ) -> List[List[List[float]]]:
        """Validate that the coordinates are valid.

        Parameters
        ----------
        v
            The coordinates to validate.

        Returns
        -------
            The validated coordinates.

        Raises
        ------
            ValueError: If the coordinates are invalid (i.e. the time is
                negative or the frequency is outside the valid range).
        """
        if len(v) < 1:
            raise ValueError("The multiline must have at least one line.")

        for line in v:
            if len(line) < 2:
                raise ValueError("Each line must have at least two points.")

            for time, frequency in line:
                if time < 0:
                    raise ValueError("The time must be positive.")

                if frequency < 0 or frequency > MAX_FREQUENCY:
                    raise ValueError(
                        f"The frequency must be between 0 and {MAX_FREQUENCY}."
                    )

        return v

    @field_validator("coordinates")
    def _each_line_is_ordered_by_time(
        cls, v: List[List[List[float]]]
    ) -> List[List[List[float]]]:
        """Validate that each line is ordered by time."""
        for line in v:
            start_time = line[0][0]
            end_time = line[-1][0]
            if not (start_time < end_time):
                raise ValueError("Each line must be ordered by time.")
        return v


class MultiPolygon(BaseGeometry):
    """MultiPolygon Geometry Class.

    The `MultiPolygon` class represents sound events within an audio recording,
    defined by multiple polygons in both time and frequency. This geometry type
    is suitable for events that are split into multiple distinct polygons,
    often due to occlusion by other sound events. `MultiPolygon` enables the
    identification and mapping of multiple separate regions within an event,
    providing a detailed representation for complex acoustic patterns, such as
    events occluded by others.

    Attributes
    ----------
    type
        The type of geometry, always set to "MultiPolygon," indicating the
        specific geometry type being utilized. This attribute ensures clear
        identification of the geometry representation and its intended purpose.
    coordinates
        The polygons of the sound event, specifying the time and frequency
        coordinates for each point in each polygon within the event. The
        `coordinates` attribute is represented as a list of lists of lists of
        lists, where each innermost list contains two float values representing
        the time and frequency of a point. All times are relative to the start
        of the recording. This format allows for the localization of multiple
        distinct regions within the recording.
    """

    type: MultiPolygonName = "MultiPolygon"

    coordinates: List[List[List[List[float]]]] = Field(
        ...,
        description="The polygons of the sound event.",
    )

    @field_validator("coordinates")
    def _validate_coordinates(
        cls, v: List[List[List[List[float]]]]
    ) -> List[List[List[List[float]]]]:
        """Validate that the coordinates are valid.

        Parameters
        ----------
        v
            The coordinates to validate.

        Returns
        -------
            The validated coordinates.

        Raises
        ------
            ValueError: If the coordinates are invalid (i.e. the time is
                negative or the frequency is outside the valid range).
        """
        if len(v) < 1:
            raise ValueError(
                "The multipolygon must have at least one polygon."
            )

        for polygon in v:
            if len(polygon) < 1:
                raise ValueError("Each polygon must have at least one ring.")

            for ring in polygon:
                if len(ring) < 3:
                    raise ValueError(
                        "Each ring must have at least three points."
                    )

                for time, frequency in ring:
                    if time < 0:
                        raise ValueError("The time must be positive.")

                    if frequency < 0 or frequency > MAX_FREQUENCY:
                        raise ValueError(
                            f"The frequency must be between 0 and "
                            f"{MAX_FREQUENCY}."
                        )

        return v


Geometry = Union[
    TimeStamp,
    TimeInterval,
    Point,
    LineString,
    Polygon,
    BoundingBox,
    MultiPoint,
    MultiLineString,
    MultiPolygon,
]
"""Geometry Type.

The Geometry type is a versatile data structure designed to pinpoint sound
events accurately within audio recordings. It encompasses a range of geometric
representations, each tailored to specific use cases within bioacoustic
research. These geometries play a fundamental role in describing the spatial
and temporal characteristics of sound events, enabling precise analysis and
interpretation.

Available Geometries:

* `TimeStamp`: Represents a sound event located at a specific point in time.
* `TimeInterval`: Describes a sound event within a specified time interval.
* `Point`: Locates a sound event at a precise time and frequency point.
* `LineString`: Defines a sound event as a trajectory in time and frequency.
* `Polygon`: Represents a complex shape in time and frequency, enclosing a
    sound event.
* `BoundingBox`: Describes a sound event within a defined time and frequency
    range.
* `MultiPoint`: Represents multiple discrete points in time and frequency as a
    single sound event.
* `MultiLineString`: Describes a sound event formed by multiple connected
    trajectories.
* `MultiPolygon`: Represents a sound event encompassed by multiple complex
    shapes.
"""


ALL_GEOMETRY_TYPES: List[Type[Geometry]] = [
    TimeStamp,
    TimeInterval,
    Point,
    LineString,
    Polygon,
    BoundingBox,
    MultiPoint,
    MultiLineString,
    MultiPolygon,
]


GEOMETRY_MAPPING: Dict[GeometryType, Type[Geometry]] = {
    geom.geom_type(): geom for geom in ALL_GEOMETRY_TYPES
}


def geometry_validate(
    obj: object,
    mode: str = "json",
) -> Geometry:
    """Convert an object to a SoundEvent geometry.

    This function is particularly useful when loading a geometry from a
    different format, such as JSON or a dictionary. This function will
    convert the object to a SoundEvent geometry, and validate it.

    Parameters
    ----------
    obj
        The object to convert to a geometry.
    mode
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

        geom_type = obj.type  # type: ignore

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
