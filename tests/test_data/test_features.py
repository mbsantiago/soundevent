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
