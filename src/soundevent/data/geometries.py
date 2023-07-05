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

* Onset: Represents a single point in time.

* Interval: Describes a time interval, indicating a range of time
within which the sound event occurs.

* Point: Represents a specific point in time and frequency,
pinpointing the exact location of the sound event.

* Line: Represents a sequence of points in time and frequency,
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
from typing import List, Tuple

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, field_validator
from shapely import geometry
from shapely.geometry.base import BaseGeometry

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

GeometryType = Literal[
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

Time = float
"""Time in seconds."""

Frequency = float
"""Frequency in Hertz."""

MAX_FREQUENCY = 5_000_000
"""The absolute maximum frequency that can be used in a geometry."""


class Geometry(BaseModel, ABC):
    """Base class for geometries.

    Notes
    -----
    Mutation of geometry objects is not allowed. This is to ensure that the
    geometry object is always in sync with the Shapely geometry object.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        frozen=True,
    )

    type: GeometryType = Field(
        ...,
        description="the type of geometry used to locate the sound event.",
    )

    _geom: BaseGeometry = PrivateAttr()
    """The Shapely geometry object representing the geometry."""

    @classmethod
    def geom_type(cls) -> str:
        """Get the geometry type.

        Returns
        -------
        str
            The Shapely geometry type.
        """
        type_field = cls.model_fields["type"]
        return type_field.default

    @property
    def geom(self) -> BaseGeometry:
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
    def _get_shapely_geometry(self) -> BaseGeometry:
        """Get the Shapely geometry object representing the geometry.

        Returns
        -------
            The Shapely geometry object representing the geometry.
        """
        raise NotImplementedError


class TimeStamp(Geometry):
    """TimeStamp geometry type.

    This geometry type is used to locate a sound event with a single time stamp.
    Useful for very short sound events that are not well represented by a
    time interval.
    """

    type: Literal["TimeStamp"] = "TimeStamp"

    coordinates: Time = Field(
        ...,
        description="The time stamp of the sound event.",
    )
    """The time stamp of the sound event.

    The time stamp is relative to the start of the recording.
    """

    def _get_shapely_geometry(self) -> BaseGeometry:
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


class TimeInterval(Geometry):
    """TimeInterval geometry type.

    This geometry type is used to locate a sound event with a time interval.
    Useful for sound events that have a clear start and end time, but that do
    not have a clear frequency range.
    """

    type: Literal["TimeInterval"] = "TimeInterval"

    coordinates: Tuple[Time, Time] = Field(
        ...,
        description="The time interval of the sound event.",
    )
    """The time interval of the sound event.

    The time interval is relative to the start of the recording.
    """

    @field_validator("coordinates")
    def validate_time_interval(cls, v: Tuple[Time, Time]) -> Tuple[Time, Time]:
        """Validate that the time interval is valid.

        Parameters
        ----------
        v : Tuple[Time, Time]
            The time interval to validate.

        Returns
        -------
            The validated time interval.

        Raises
        ------
            ValueError: If the time interval is invalid (i.e. the start time is
                after the end time).
        """
        if v[0] > v[1]:
            raise ValueError("The start time must be before the end time.")
        return v

    def _get_shapely_geometry(self) -> BaseGeometry:
        """Get the Shapely geometry object representing the sound event.

        Returns
        -------
            The Shapely geometry object representing the sound event.
        """
        start_time, end_time = self.coordinates
        return geometry.box(start_time, 0, end_time, MAX_FREQUENCY)


class Point(Geometry):
    """Point geometry type.

    This geometry type is used to locate a sound event with a single point in
    time and frequency.
    """

    type: Literal["Point"] = "Point"

    coordinates: Tuple[Time, Frequency] = Field(
        ...,
        description="The points of the sound event.",
    )
    """The points of the sound event.

    The time is relative to the start of the recording.

    """

    def _get_shapely_geometry(self) -> BaseGeometry:
        """Get the Shapely geometry object representing the geometry.

        Returns
        -------
            The Shapely geometry object representing the geometry.
        """
        return geometry.Point(self.coordinates)


class LineString(Geometry):
    """LineString geometry type.

    This geometry type is used to locate a sound event with a line in time and
    frequency. Useful to lcoate with detail sounds that have a clear frequency
    trajectory.
    """

    type: Literal["LineString"] = "LineString"

    coordinates: List[Tuple[Time, Frequency]] = Field(
        ...,
        description="The line of the sound event.",
    )
    """The line of the sound event.

    Each line should be ordered by time.

    All times are relative to the start of the recording."""

    def _get_shapely_geometry(self) -> BaseGeometry:
        """Get the Shapely geometry object representing the geometry.

        Returns
        -------
            The Shapely geometry object representing the geometry.
        """
        return geometry.LineString(self.coordinates)

    @field_validator("coordinates")
    def has_at_least_two_points(
        cls, v: List[Tuple[Time, Frequency]]
    ) -> List[Tuple[Time, Frequency]]:
        """Validate that the line has at least two points."""
        if len(v) < 2:
            raise ValueError("The line must have at least two points.")
        return v

    @field_validator("coordinates")
    def is_ordered_by_time(
        cls, v: List[Tuple[Time, Frequency]]
    ) -> List[Tuple[Time, Frequency]]:
        """Validate that the line is ordered by time."""
        if not all(v[i][0] <= v[i + 1][0] for i in range(len(v) - 1)):
            raise ValueError("The line must be ordered by time.")
        return v


class Polygon(Geometry):
    """Polygon geometry type.

    This geometry type is used to locate a sound event with a polygon in time
    and frequency. Useful to locate with detail sounds that have a clear
    frequency trajectory and that are bounded by a clear start and end time.
    """

    type: Literal["Polygon"] = "Polygon"

    coordinates: List[List[Tuple[Time, Frequency]]] = Field(
        ...,
        description="The polygon of the sound event.",
    )
    """The polygon of the sound event.

    All times are relative to the start of the recording."""

    @field_validator("coordinates")
    def has_at_least_one_ring(
        cls, v: List[List[Tuple[Time, Frequency]]]
    ) -> List[List[Tuple[Time, Frequency]]]:
        """Validate that the polygon has at least one ring."""
        if len(v) == 0:
            raise ValueError("The polygon must have at least one ring.")
        return v

    def _get_shapely_geometry(self) -> BaseGeometry:
        """Get the Shapely geometry object representing the geometry.

        Returns
        -------
            The Shapely geometry object representing the geometry.
        """
        shell = self.coordinates[0]
        holes = self.coordinates[1:]
        return geometry.Polygon(shell, holes)


class BoundingBox(Geometry):
    """BoundingBox geometry type.

    This geometry type is used to locate a sound event with a bounding box in
    time and frequency. Useful to locate sounds that have a clear frequency
    range and start and stop times.
    """

    type: Literal["BoundingBox"] = "BoundingBox"

    coordinates: Tuple[Time, Frequency, Time, Frequency] = Field(
        ...,
        description="The bounding box of the sound event.",
    )
    """The bounding box of the sound event.

    The format is (start time, start frequency, end time, end frequency).
    All times are relative to the start of the recording.
    """

    @field_validator("coordinates")
    def validate_bounding_box(
        cls,
        v: Tuple[Time, Frequency, Time, Frequency],
    ) -> Tuple[Time, Frequency, Time, Frequency]:
        """Validate that the bounding box is valid."""
        if v[0] > v[2]:
            raise ValueError("The start time must be before the end time.")

        if v[1] > v[3]:
            raise ValueError(
                "The start frequency must be before the end frequency."
            )

        return v

    def _get_shapely_geometry(self) -> BaseGeometry:
        """Get the Shapely geometry object representing the geometry."""
        start_time, start_frequency, end_time, end_frequency = self.coordinates
        return geometry.box(
            start_time,
            start_frequency,
            end_time,
            end_frequency,
        )


class MultiPoint(Geometry):
    """MultiPoint geometry type.

    This geometry type is used to locate a sound event with multiple points in
    time and frequency. Useful to locate multiple interesting points that
    together form a sound event.
    """

    type: Literal["MultiPoint"] = "MultiPoint"

    coordinates: List[Tuple[Time, Frequency]] = Field(
        ...,
        description="The points of the sound event.",
    )
    """The points of the sound event.

    All times are relative to the start of the recording."""

    def _get_shapely_geometry(self) -> BaseGeometry:
        """Get the Shapely geometry object representing the geometry.

        Returns
        -------
            The Shapely geometry object representing the geometry.
        """
        return geometry.MultiPoint(self.coordinates)


class MultiLineString(Geometry):
    """MultiLineString geometry type.

    This geometry type is used to locate a sound event with multiple lines in
    time and frequency. Useful to locate multiple interesting lines that
    together form a sound event. For example, a sound event that has multiple
    harmonics.
    """

    type: Literal["MultiLineString"] = "MultiLineString"

    coordinates: List[List[Tuple[Time, Frequency]]] = Field(
        ...,
        description="The lines of the sound event.",
    )
    """The lines of the sound event.

    All times are relative to the start of the recording."""

    def _get_shapely_geometry(self) -> BaseGeometry:
        """Get the Shapely geometry object representing the geometry.

        Returns
        -------
            The Shapely geometry object representing the geometry.
        """
        return geometry.MultiLineString(self.coordinates)

    @field_validator("coordinates")
    def has_at_least_one_line(
        cls, v: List[List[Tuple[Time, Frequency]]]
    ) -> List[List[Tuple[Time, Frequency]]]:
        """Validate that the multiline has at least one line."""
        if len(v) == 0:
            raise ValueError("The multiline must have at least one line.")
        return v

    @field_validator("coordinates")
    def each_line_has_at_least_two_points(
        cls, v: List[List[Tuple[Time, Frequency]]]
    ) -> List[List[Tuple[Time, Frequency]]]:
        """Validate that each line has at least two points."""
        if not all(len(line) >= 2 for line in v):
            raise ValueError("Each line must have at least two points.")
        return v

    @field_validator("coordinates")
    def each_line_is_ordered_by_time(
        cls, v: List[List[Tuple[Time, Frequency]]]
    ) -> List[List[Tuple[Time, Frequency]]]:
        """Validate that each line is ordered by time."""
        for line in v:
            if not all(
                line[i][0] <= line[i + 1][0] for i in range(len(line) - 1)
            ):
                raise ValueError("Each line must be ordered by time.")
        return v


class MultiPolygon(Geometry):
    """MultiPolygon geometry type.

    This geometry type is used to locate a sound event with multiple polygons in
    time and frequency. Useful to locate multiple interesting polygons that
    together form a sound event. For example sound events that have been
    occluded by other sound events and that are therefore split into multiple
    polygons.
    """

    type: Literal["MultiPolygon"] = "MultiPolygon"

    coordinates: List[List[List[Tuple[Time, Frequency]]]] = Field(
        ...,
        description="The polygons of the sound event.",
    )
    """The polygons of the sound event.

    All times are relative to the start of the recording."""

    @field_validator("coordinates")
    def has_at_least_one_polygon(
        cls, v: List[List[List[Tuple[Time, Frequency]]]]
    ) -> List[List[List[Tuple[Time, Frequency]]]]:
        """Validate that the multipolygon has at least one polygon."""
        if len(v) == 0:
            raise ValueError(
                "The multipolygon must have at least one polygon."
            )
        return v

    @field_validator("coordinates")
    def each_polygon_has_at_least_one_ring(
        cls, v: List[List[List[Tuple[Time, Frequency]]]]
    ) -> List[List[List[Tuple[Time, Frequency]]]]:
        """Validate that each polygon has at least one ring."""
        for polygon in v:
            if len(polygon) == 0:
                raise ValueError("Each polygon must have at least one ring.")
        return v

    def _get_shapely_geometry(self) -> BaseGeometry:
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
