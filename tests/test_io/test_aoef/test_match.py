"""Test suite for AOEF Match Adapter."""

from soundevent import data
from soundevent.io.aoef.match import MatchAdapter, MatchObject


def test_match_can_be_converted_to_aoef(
    match: data.Match,
    match_adapter: MatchAdapter,
):
    """Test that a match can be converted to AOEF."""
    aoef = match_adapter.to_aoef(match)
    assert isinstance(aoef, MatchObject)


def test_match_is_recovered(
    match: data.Match,
    match_adapter: MatchAdapter,
):
    """Test that a match is recovered."""
    aoef = match_adapter.to_aoef(match)
    recovered = match_adapter.to_soundevent(aoef)
    assert match == recovered
