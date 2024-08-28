"""Test suite for the soundevent.data.tags module."""

import pytest

from soundevent import data, terms


def test_tags_are_hashable():
    """Test that tags are hashable."""
    tag = data.Tag(
        term=terms.scientific_name,
        value="value",
    )
    assert hash(tag) == hash((tag.term, tag.value))


def test_can_find_tag_by_key_in_list(random_tags):
    tags = random_tags(10)
    tag = tags[5]
    found = data.find_tag(tags, term=tag.term)
    assert tag == found


def test_find_tag_returns_none_if_key_not_found(random_tags):
    tags = random_tags(10)
    found = data.find_tag(tags, label="unlikely_key")
    assert found is None


def test_can_create_tag_without_term_and_with_key():
    tag = data.Tag(key="key", value="value")  # type: ignore
    assert isinstance(tag.term, data.Term)
    assert tag.term.label == "key"
    assert tag.term.name == "soundevent:key"


def test_shows_deprecation_warning_when_using_key():
    with pytest.warns(DeprecationWarning):
        tag = data.Tag(key="key", value="value")  # type: ignore

    tag = data.Tag(term=terms.scientific_name, value="Myotis myotis")
    with pytest.warns(DeprecationWarning):
        key = tag.key

    assert key == terms.scientific_name.label
