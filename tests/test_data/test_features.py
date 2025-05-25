"""Test suite for the soundevent.data.features module."""

import pytest

from soundevent import data, terms


def test_features_are_hashable():
    """Test that features are hashable."""
    tag = data.Feature(term=terms.duration, value=10)
    assert hash(tag) == hash((tag.term, tag.value))


def test_can_find_feature_by_key_in_list(random_features):
    features = random_features(10)
    feature = features[5]
    found = data.find_feature(features, term=feature.term)
    assert feature == found


def test_find_feature_returns_none_if_key_not_found(random_features):
    features = random_features(10)
    found = data.find_feature(features, label="unlikely_key")
    assert found is None


def test_can_create_feature_without_term_and_with_key():
    feature = data.Feature(name="name", value=10)  # type: ignore
    assert isinstance(feature.term, data.Term)
    assert feature.term.label == "name"
    assert feature.term.name == "soundevent:name"


def test_shows_deprecation_warning_when_using_key():
    with pytest.warns(DeprecationWarning):
        feature = data.Feature(name="key", value=10)  # type: ignore

    feature = data.Feature(term=terms.duration, value=50)
    with pytest.warns(DeprecationWarning):
        name = feature.name

    assert name == terms.duration.label


example_features = [
    data.Feature(name="name1", value=1),  # type: ignore
    data.Feature(name="name2", value=2),  # type: ignore
    data.Feature(name="name3", value=3),  # type: ignore
    data.Feature(name="name4", value=4),  # type: ignore
    data.Feature(name="name5", value=5),  # type: ignore
    data.Feature(term=terms.high_freq, value=6),
]


def test_can_find_feature_value_by_name():
    value = data.find_feature_value(example_features, name="name3")
    assert value == 3


def test_can_find_feature_value_by_term():
    value = data.find_feature_value(example_features, term=terms.high_freq)
    assert value == 6


def test_can_find_feature_by_term_name():
    value = data.find_feature_value(example_features, term_name="ac:freqHigh")
    assert value == 6


def test_can_find_feature_value_by_term_label():
    value = data.find_feature_value(
        example_features, term_label="Upper frequency bound"
    )
    assert value == 6


def test_find_feature_value_returns_none_if_not_found():
    value = data.find_feature_value(example_features, name="non-existent")
    assert value is None


def test_find_feature_value_returns_default_if_not_found():
    value = data.find_feature_value(
        example_features, name="non-existent", default=42
    )
    assert value == 42


def test_find_feature_value_raises_error_if_requested_and_not_found():
    with pytest.raises(ValueError):
        data.find_feature_value(
            example_features, name="non-existent", raises=True
        )


def test_find_feature_fails_if_no_criteria_provided():
    with pytest.raises(ValueError):
        data.find_feature(example_features)


def test_find_feature_fails_if_multiple_criteria_provided():
    with pytest.raises(ValueError):
        data.find_feature(
            example_features,
            term_label="Upper frequency bound",
            term_name="ac:freqHigh",
        )
