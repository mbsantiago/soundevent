"""Common fixtures for testing geometry functions."""

import pytest

from soundevent import data


@pytest.fixture
def time_stamp() -> data.TimeStamp:
    return data.TimeStamp(coordinates=1)


@pytest.fixture
def time_interval() -> data.TimeInterval:
    return data.TimeInterval(coordinates=[0.5, 1.5])


@pytest.fixture
def point() -> data.Point:
    return data.Point(coordinates=[1, 440])


@pytest.fixture
def linestring() -> data.LineString:
    return data.LineString(coordinates=[[0.5, 400], [1, 440], [1.5, 800]])


@pytest.fixture
def bounding_box() -> data.BoundingBox:
    return data.BoundingBox(coordinates=[0.5, 400, 1.5, 800])


@pytest.fixture
def polygon() -> data.Polygon:
    return data.Polygon(
        coordinates=[[[0.5, 400], [1, 600], [1.5, 800], [1, 440], [0.5, 400]]]
    )


@pytest.fixture
def multi_point() -> data.MultiPoint:
    return data.MultiPoint(coordinates=[[1, 440], [1.5, 800], [0.5, 400]])


@pytest.fixture
def multi_line_string() -> data.MultiLineString:
    return data.MultiLineString(
        coordinates=[
            [[0.5, 400], [1, 440], [1.5, 800]],
            [[0.5, 440], [1, 600], [1.5, 880]],
        ]
    )


@pytest.fixture
def multi_polygon() -> data.MultiPolygon:
    return data.MultiPolygon(
        coordinates=[
            [[[0.5, 400], [1, 600], [1.5, 800], [1, 440], [0.5, 400]]],
            [[[0.5, 800], [1, 1200], [1.5, 1600], [1, 880], [0.5, 800]]],
        ]
    )
