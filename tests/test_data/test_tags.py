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


example_tags = [
    data.Tag(key="key1", value="value1"),  # type: ignore
    data.Tag(key="key2", value="value2"),  # type: ignore
    data.Tag(key="key3", value="value3"),  # type: ignore
    data.Tag(key="key4", value="value4"),  # type: ignore
    data.Tag(key="key5", value="value5"),  # type: ignore
    data.Tag(term=terms.scientific_name, value="species"),
]


def test_can_find_tag_value_by_key():
    value = data.find_tag_value(example_tags, key="key3")
    assert value == "value3"


def test_can_find_tag_value_by_term():
    value = data.find_tag_value(example_tags, term=terms.scientific_name)
    assert value == "species"


def test_can_find_tag_by_term_name():
    value = data.find_tag_value(example_tags, term_name="dwc:scientificName")
    assert value == "species"


def test_can_find_tag_value_by_term_label():
    value = data.find_tag_value(
        example_tags, term_label="Scientific Taxon Name"
    )
    assert value == "species"


def test_find_tag_value_returns_none_if_not_found():
    value = data.find_tag_value(example_tags, key="non-existent")
    assert value is None


def test_find_tag_value_returns_default_if_not_found():
    value = data.find_tag_value(
        example_tags, key="non-existent", default="test"
    )
    assert value == "test"


def test_find_tag_value_raises_error_if_requested_and_not_found():
    with pytest.raises(ValueError):
        data.find_tag_value(example_tags, key="non-existent", raises=True)


def test_find_tag_fails_if_no_criteria_provided():
    with pytest.raises(ValueError):
        data.find_tag(example_tags)


def test_find_tag_fails_if_multiple_criteria_provided():
    with pytest.raises(ValueError):
        data.find_tag(
            example_tags,
            term_label="Scientific Taxon Name",
            term_name="dwc:scientificName",
        )
