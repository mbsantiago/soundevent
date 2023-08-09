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
import sys
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Type, Union

import shapely
from pydantic import BaseModel, Field, PrivateAttr, field_validator
from shapely import geometry
from shapely.geometry.base import BaseGeometry as ShapelyBaseGeometry

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = [
    "Time",
    "Frequency",
    "GeometryType",
    "MAX_FREQUENCY",
    "Geometry",
    "TimeStamp",
    "TimeInterval",
    "BoundingBox",
    "Point",
    "LineString",
    "Polygon",
    "MultiPoint",
    "MultiLineString",
    "MultiPolygon",
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
    """Base class for geometries.

    Notes
    -----
    Mutation of geometry objects is not allowed. This is to ensure that the
    geometry object is always in sync with the Shapely geometry object.
    """

    type: GeometryType = Field(
        description="the type of geometry used to locate the sound event.",
        frozen=True,
        include=True,
    )

    coordinates: Union[float, List] = Field(
        description="the coordinates of the geometry.",
        frozen=True,
        include=True,
    )

    _geom: ShapelyBaseGeometry = PrivateAttr()
    """The Shapely geometry object representing the geometry."""

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

    @property
    def geom(self) -> ShapelyBaseGeometry:
        """Get the Shapely geometry object representing the geometry.

        Returns
        -------
            The Shapely geometry object representing the geometry.
        """
        return self._geom

    @property
    def bounds(self) -> Tuple[Time, Frequency, Time, Frequency]:
        """Get the bounds of the geometry.

        Returns
        -------
        Tuple[Time, Frequency, Time, Frequency]
            The bounds of the geometry.
        """
        return self._geom.bounds

    def __init__(self, **data):
        """Initialize the geometry."""
        super().__init__(**data)
        self._geom = self._get_shapely_geometry()

    @abstractmethod
    def _get_shapely_geometry(self) -> ShapelyBaseGeometry:
        """Get the Shapely geometry object representing the geometry.

        Returns
        -------
            The Shapely geometry object representing the geometry.
        """
        raise NotImplementedError

    def _repr_html_(self) -> str:
        """Represent the geometry as HTML.

        Returns
        -------
        str
            The HTML representation of the geometry.
        """
        start_time, low_freq, end_time, high_freq = self.bounds

        duration = end_time - start_time
        bandwidth = high_freq - low_freq

        factor = [
            1 / duration if duration > 0 else 1,
            1 / bandwidth if bandwidth > 0 else 1,
        ]

        transformed = shapely.transform(
            self.geom,
            lambda x: x * factor,
        )._repr_svg_()

        style = (
            "display: inline-block; "
            "position: relative;"
            "width: 100px; "
            "height: 100px; "
        )

        def axis_label(
            label: float,
            top: bool = False,
            left: bool = True,
            axis: str = "time",
        ) -> str:
            outer_style = "; ".join(
                [
                    "position: absolute",
                    "top: 0; " if top else "bottom: 0",
                    "left: 0; " if left else "right: 0",
                    "transform: translate(-105%, 0)"
                    if axis == "freq"
                    else "transform: translate(0, 100%)",
                ]
            )

            inner_style = "; ".join(
                [
                    "display: inline",
                    "vertical-align: top"
                    if axis == "time"
                    else "vertical-align: bottom",
                ]
            )

            label_str = f"{label:.2f}" if axis == "time" else f"{label:.0f}"

            return (
                f'<div style="{outer_style}">'
                f'<small style="{inner_style}">{label_str}</small>'
                "</div>"
            )

        return (
            f'<div style="{style}">'
            f'{axis_label(start_time, left=True, axis="time")}'
            f'{axis_label(end_time, left=False, axis="time")}'
            f'{axis_label(low_freq, top=False, axis="freq")}'
            f'{axis_label(high_freq, top=True, axis="freq")}'
            f"{transformed}"
            "</div>"
        )


class TimeStamp(BaseGeometry):
    """TimeStamp geometry type.

    This geometry type is used to locate a sound event with a single time stamp.
    Useful for very short sound events that are not well represented by a
    time interval.
    """

    type: TimeStampName = "TimeStamp"

    coordinates: Time = Field(
        ...,
        description="The time stamp of the sound event.",
    )
    """The time stamp of the sound event.

    The time stamp is relative to the start of the recording.
    """

    def _get_shapely_geometry(self) -> ShapelyBaseGeometry:
        """Get the Shapely geometry object representing the geometry.

        Returns
        -------
            The Shapely geometry object representing the geometry.
        """
        return geometry.box(
            self.coordinates,
            0,
            self.coordinates,
            MAX_FREQUENCY,
        )

    def _repr_html_(self) -> str:
        """Represent the geometry as HTML.

        Returns
        -------
        str
            The HTML representation of the geometry.
        """
        time = self.coordinates

        label_style = "; ".join(
            [
                "position: absolute",
                "bottom: 0",
                "transform: translate(0, 100%)",
            ]
        )

        inner_style = "; ".join(
            [
                "display: inline",
                "vertical-align: bottom",
            ]
        )

        style = "; ".join(
            [
                "display: inline-block",
                "position: relative",
                "width: 100px",
                "height: 100px",
            ]
        )

        geom_svg = self.geom._repr_svg_()

        return (
            f'<div style="{style}">'
            f'<div style="{label_style}">'
            f'<small style="{inner_style}">{time}</small>'
            "</div>"
            f"{geom_svg}"
            "</div>"
        )


class TimeInterval(BaseGeometry):
    """TimeInterval geometry type.

    This geometry type is used to locate a sound event with a time interval.
    Useful for sound events that have a clear start and end time, but that do
    not have a clear frequency range.
    """

    type: TimeIntervalName = "TimeInterval"

    coordinates: List[Time] = Field(
        description="The time interval of the sound event.",
    )
    """The time interval of the sound event.

    The time interval is relative to the start of the recording.
    """

    @field_validator("coordinates")
    def validate_time_interval(cls, v: List[Time]) -> List[Time]:
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

    def _get_shapely_geometry(self) -> ShapelyBaseGeometry:
        """Get the Shapely geometry object representing the sound event.

        Returns
        -------
            The Shapely geometry object representing the sound event.
        """
        start_time, end_time = self.coordinates
        return geometry.box(start_time, 0, end_time, MAX_FREQUENCY)


class Point(BaseGeometry):
    """Point geometry type.

    This geometry type is used to locate a sound event with a single point in
    time and frequency.
    """

    type: PointName = "Point"

    coordinates: List[float] = Field(
        ...,
        description="The points of the sound event.",
    )
    """The points of the sound event.

    The time is relative to the start of the recording.

    """

    @field_validator("coordinates")
    def validate_coordinates(cls, v: List[float]) -> List[float]:
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

    def _get_shapely_geometry(self) -> ShapelyBaseGeometry:
        """Get the Shapely geometry object representing the geometry.

        Returns
        -------
            The Shapely geometry object representing the geometry.
        """
        return geometry.Point(self.coordinates)


class LineString(BaseGeometry):
    """LineString geometry type.

    This geometry type is used to locate a sound event with a line in time and
    frequency. Useful to lcoate with detail sounds that have a clear frequency
    trajectory.
    """

    type: LineStringName = "LineString"

    coordinates: List[List[float]] = Field(
        ...,
        description="The line of the sound event.",
    )
    """The line of the sound event.

    Each line should be ordered by time.

    All times are relative to the start of the recording."""

    def _get_shapely_geometry(self) -> ShapelyBaseGeometry:
        """Get the Shapely geometry object representing the geometry.

        Returns
        -------
            The Shapely geometry object representing the geometry.
        """
        return geometry.LineString(self.coordinates)

    @field_validator("coordinates")
    def validate_coordinates(cls, v: List[List[float]]) -> List[List[float]]:
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
    def is_ordered_by_time(cls, v: List[List[float]]) -> List[List[float]]:
        """Validate that the line is ordered by time."""
        if not all(v[i][0] <= v[i + 1][0] for i in range(len(v) - 1)):
            raise ValueError("The line must be ordered by time.")
        return v


class Polygon(BaseGeometry):
    """Polygon geometry type.

    This geometry type is used to locate a sound event with a polygon in time
    and frequency. Useful to locate with detail sounds that have a clear
    frequency trajectory and that are bounded by a clear start and end time.
    """

    type: PolygonName = "Polygon"

    coordinates: List[List[List[float]]] = Field(
        ...,
        description="The polygon of the sound event.",
    )
    """The polygon of the sound event.

    All times are relative to the start of the recording."""

    @field_validator("coordinates")
    def validate_coordinates(
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

    def _get_shapely_geometry(self) -> ShapelyBaseGeometry:
        """Get the Shapely geometry object representing the geometry.

        Returns
        -------
            The Shapely geometry object representing the geometry.
        """
        shell = self.coordinates[0]
        holes = self.coordinates[1:]
        return geometry.Polygon(shell, holes)


class BoundingBox(BaseGeometry):
    """BoundingBox geometry type.

    This geometry type is used to locate a sound event with a bounding box in
    time and frequency. Useful to locate sounds that have a clear frequency
    range and start and stop times.
    """

    type: BoundingBoxName = "BoundingBox"

    coordinates: List[float] = Field(
        ...,
        description="The bounding box of the sound event.",
    )
    """The bounding box of the sound event.

    The format is (start time, start frequency, end time, end frequency).
    All times are relative to the start of the recording.
    """

    @field_validator("coordinates")
    def validate_coordinates(cls, v: List[float]) -> List[float]:
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
            raise ValueError("The start time must be before the end time.")

        if low_freq > high_freq:
            raise ValueError(
                "The start frequency must be before the end frequency."
            )

        return v

    def _get_shapely_geometry(self) -> ShapelyBaseGeometry:
        """Get the Shapely geometry object representing the geometry."""
        start_time, start_frequency, end_time, end_frequency = self.coordinates
        return geometry.box(
            start_time,
            start_frequency,
            end_time,
            end_frequency,
        )


class MultiPoint(BaseGeometry):
    """MultiPoint geometry type.

    This geometry type is used to locate a sound event with multiple points in
    time and frequency. Useful to locate multiple interesting points that
    together form a sound event.
    """

    type: MultiPointName = "MultiPoint"

    coordinates: List[List[float]] = Field(
        ...,
        description="The points of the sound event.",
    )
    """The points of the sound event.

    All times are relative to the start of the recording."""

    @field_validator("coordinates")
    def validate_coordinates(cls, v: List[List[float]]) -> List[List[float]]:
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

    def _get_shapely_geometry(self) -> ShapelyBaseGeometry:
        """Get the Shapely geometry object representing the geometry.

        Returns
        -------
            The Shapely geometry object representing the geometry.
        """
        return geometry.MultiPoint(self.coordinates)


class MultiLineString(BaseGeometry):
    """MultiLineString geometry type.

    This geometry type is used to locate a sound event with multiple lines in
    time and frequency. Useful to locate multiple interesting lines that
    together form a sound event. For example, a sound event that has multiple
    harmonics.
    """

    type: MultiLineStringName = "MultiLineString"

    coordinates: List[List[List[float]]] = Field(
        ...,
        description="The lines of the sound event.",
    )
    """The lines of the sound event.

    All times are relative to the start of the recording."""

    def _get_shapely_geometry(self) -> ShapelyBaseGeometry:
        """Get the Shapely geometry object representing the geometry.

        Returns
        -------
            The Shapely geometry object representing the geometry.
        """
        return geometry.MultiLineString(self.coordinates)

    @field_validator("coordinates")
    def validate_coordinates(
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
    def each_line_is_ordered_by_time(
        cls, v: List[List[List[float]]]
    ) -> List[List[List[float]]]:
        """Validate that each line is ordered by time."""
        for line in v:
            if not all(
                line[i][0] <= line[i + 1][0] for i in range(len(line) - 1)
            ):
                raise ValueError("Each line must be ordered by time.")
        return v


class MultiPolygon(BaseGeometry):
    """MultiPolygon geometry type.

    This geometry type is used to locate a sound event with multiple polygons in
    time and frequency. Useful to locate multiple interesting polygons that
    together form a sound event. For example sound events that have been
    occluded by other sound events and that are therefore split into multiple
    polygons.
    """

    type: MultiPolygonName = "MultiPolygon"

    coordinates: List[List[List[List[float]]]] = Field(
        ...,
        description="The polygons of the sound event.",
    )
    """The polygons of the sound event.

    All times are relative to the start of the recording."""

    @field_validator("coordinates")
    def validate_coordinates(
        cls, v: List[List[List[List[float]]]]
    ) -> List[List[List[List[float]]]]:
        """Validate that the coordinates are valid.

        Parameters
        ----------
        v : List[List[List[List[float]]]]
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

    def _get_shapely_geometry(self) -> ShapelyBaseGeometry:
        """Get the Shapely geometry object representing the geometry.

        Returns
        -------
            The Shapely geometry object representing the geometry.
        """
        polgons = []
        for poly in self.coordinates:
            shell = poly[0]
            holes = poly[1:]
            polygon = geometry.Polygon(shell, holes)
            polgons.append(polygon)
        return geometry.MultiPolygon(polgons)


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
