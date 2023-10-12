"""Test suite for the soundevent.data.tags module."""

from soundevent import data


def test_tags_are_hashable():
    """Test that tags are hashable."""
    tag = data.Tag(
        key="key",
        value="value",
    )
    assert hash(tag) == hash((tag.key, tag.value))


def test_can_find_tag_by_key_in_list(random_tags):
    tags = random_tags(10)
    tag = tags[5]
    found = data.find_tag(tags, tag.key)
    assert tag == found


def test_find_tag_returns_none_if_key_not_found(random_tags):
    tags = random_tags(10)
    found = data.find_tag(tags, "unlikely_key")
    assert found is None
