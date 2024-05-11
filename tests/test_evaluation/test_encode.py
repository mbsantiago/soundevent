"""Test suite for the soundevent.evaluation.ecoding module."""

from typing import Callable, Sequence

import numpy as np
import pytest

from soundevent import data
from soundevent.evaluation import (
    classification_encoding,
    create_tag_encoder,
    multilabel_encoding,
    prediction_encoding,
)
from soundevent.evaluation.encoding import Encoder


@pytest.fixture
def tags(
    random_tags: Callable[[int], Sequence[data.Tag]],
) -> Sequence[data.Tag]:
    """Tags for testing."""
    return random_tags(10)


@pytest.fixture
def encoder(
    tags: Sequence[data.Tag],
) -> Encoder:
    """Encode for testing."""
    target_tags = tags[:5]
    return create_tag_encoder(target_tags)


def test_classification_encoding(
    tags: Sequence[data.Tag],
    encoder: Encoder,
):
    """Test encoding objects with tags."""
    encoded = classification_encoding(
        tags=[tags[3]],
        encoder=encoder,
    )

    assert encoded == 3


def test_classification_encoding_with_extra_tags(
    tags: Sequence[data.Tag],
    encoder: Encoder,
):
    """Test encoding objects with extra tags."""
    encoded = classification_encoding(
        tags=[tags[7], tags[3]],
        encoder=encoder,
    )

    assert encoded == 3


def test_classification_encoding_favours_first(
    tags: Sequence[data.Tag],
    encoder: Encoder,
):
    """Test that the first tag is favoured when multiple tags are present."""
    encoded = classification_encoding(
        tags=[tags[3], tags[1]],
        encoder=encoder,
    )

    assert encoded == 3


def test_classification_encoding_returns_none_if_missing(
    tags: Sequence[data.Tag],
    encoder: Encoder,
):
    """Test that the encoder returns None if no tags are present."""
    encoded = classification_encoding(
        tags=[tags[8]],
        encoder=encoder,
    )
    assert encoded is None


def test_prediction_encoding(
    tags: Sequence[data.Tag],
    encoder: Encoder,
):
    """Test encoding predicted tags."""
    encoded = prediction_encoding(
        tags=[data.PredictedTag(tag=tags[3], score=0.7)],
        encoder=encoder,
    )

    assert isinstance(encoded, np.ndarray)
    assert encoded.shape == (5,)
    assert np.isclose(encoded[3], 0.7)
    assert (encoded == 0).sum() == 4


def test_prediction_encoding_with_extra_tags(
    tags: Sequence[data.Tag],
    encoder: Encoder,
):
    """Test encoding predicted tags with extra tags."""
    encoded = prediction_encoding(
        tags=[
            data.PredictedTag(tag=tags[7], score=0.7),
            data.PredictedTag(tag=tags[3], score=0.9),
        ],
        encoder=encoder,
    )

    assert isinstance(encoded, np.ndarray)
    assert encoded.shape == (5,)
    assert np.isclose(encoded[3], 0.9)
    assert (encoded == 0).sum() == 4


def test_prediction_encoding_is_zero_if_missing(
    tags: Sequence[data.Tag],
    encoder: Encoder,
):
    """Test that the encoder returns zero if no tags are present."""
    encoded = prediction_encoding(
        tags=[data.PredictedTag(tag=tags[8], score=0.7)],
        encoder=encoder,
    )

    assert isinstance(encoded, np.ndarray)
    assert encoded.shape == (5,)
    assert (encoded == 0).all()


def test_prediction_encoding_with_multiple_tags(
    tags: Sequence[data.Tag],
    encoder: Encoder,
):
    """Test that the encoder returns zero if no tags are present."""
    encoded = prediction_encoding(
        tags=[
            data.PredictedTag(tag=tags[3], score=0.7),
            data.PredictedTag(tag=tags[1], score=0.9),
        ],
        encoder=encoder,
    )

    assert isinstance(encoded, np.ndarray)
    assert encoded.shape == (5,)
    assert np.isclose(encoded[3], 0.7)
    assert np.isclose(encoded[1], 0.9)
    assert (encoded == 0).sum() == 3


def test_multilabel_encoding(
    tags: Sequence[data.Tag],
    encoder: Encoder,
):
    """Test encoding multilabel tags."""
    encoded = multilabel_encoding(
        tags=[tags[3]],
        encoder=encoder,
    )

    assert isinstance(encoded, np.ndarray)
    assert encoded.shape == (5,)
    assert encoded[3] == 1
    assert (encoded == 0).sum() == 4


def test_multilabel_encoding_with_multiple_tags(
    tags: Sequence[data.Tag],
    encoder: Encoder,
):
    """Test encoding multilabel tags with multiple tags."""
    encoded = multilabel_encoding(
        tags=[tags[3], tags[1]],
        encoder=encoder,
    )

    assert isinstance(encoded, np.ndarray)
    assert encoded.shape == (5,)
    assert encoded[3] == 1
    assert encoded[1] == 1
    assert (encoded == 0).sum() == 3


def test_multilabel_encoding_with_extra_tags(
    tags: Sequence[data.Tag],
    encoder: Encoder,
):
    """Test encoding multilabel tags with extra tags."""
    encoded = multilabel_encoding(
        tags=[tags[7], tags[3]],
        encoder=encoder,
    )

    assert isinstance(encoded, np.ndarray)
    assert encoded.shape == (5,)
    assert encoded[3] == 1
    assert (encoded == 0).sum() == 4


def test_multilabel_encoding_is_zero_if_missing(
    tags: Sequence[data.Tag],
    encoder: Encoder,
):
    """Test that the encoder returns zero if no tags are present."""
    encoded = multilabel_encoding(
        tags=[tags[8]],
        encoder=encoder,
    )

    assert isinstance(encoded, np.ndarray)
    assert encoded.shape == (5,)
    assert (encoded == 0).all()
