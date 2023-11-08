"""Test suite for the affinity module."""

import math

from soundevent.data import TimeStamp
from soundevent.evaluation import compute_affinity


def test_affinity_between_time_stamps():
    """Test computation of geometric affinity between two timestamps."""
    ts1 = TimeStamp(coordinates=0.0)
    ts2 = TimeStamp(coordinates=1.0)

    assert compute_affinity(ts1, ts1) == 1
    assert compute_affinity(ts1, ts2) == 0


def test_default_time_buffer():
    ts1 = TimeStamp(coordinates=0.0)
    ts2 = TimeStamp(coordinates=0.01)
    ts3 = TimeStamp(coordinates=0.02)
    assert math.isclose(compute_affinity(ts1, ts2), 0.5)
    assert math.isclose(compute_affinity(ts1, ts3), 0)
