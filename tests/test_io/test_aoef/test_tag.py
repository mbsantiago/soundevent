"""Test suite for AOEF Tag Adapter."""

from soundevent import data
from soundevent.io.aoef.tag import TagAdapter, TagObject


def test_tag_can_be_converted_to_aoef(
    tag: data.Tag,
    tag_adapter: TagAdapter,
):
    """Test that a tag can be converted to AOEF."""
    aoef = tag_adapter.to_aoef(tag)
    assert isinstance(aoef, TagObject)


def test_tag_is_recovered(
    tag: data.Tag,
    tag_adapter: TagAdapter,
):
    """Test that a tag is recovered."""
    aoef = tag_adapter.to_aoef(tag)
    recovered = tag_adapter.to_soundevent(aoef)
    assert tag == recovered
