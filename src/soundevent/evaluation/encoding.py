"""Tag Encoder Module."""

from typing import Optional, Protocol, Sequence

import numpy as np

from soundevent import data

__all__ = [
    "classification_encoding",
    "multilabel_encoding",
    "prediction_encoding",
    "create_tag_encoder",
    "Encoder",
]


class Encoder(Protocol):
    """A callable object that maps tags into integers.

    This protocol defines the structure of an encoder function, which maps
    tags into integers. The encoder function takes a `data.Tag` object as input
    and returns an optional integer encoding. If the encoder returns None for
    a tag, it will be skipped.

    Attributes
    ----------
    num_classes : int
        The total number of classes for the encoding.

    """

    num_classes: int

    def encode(self, tag: data.Tag) -> Optional[int]:
        """Encode a tag into an integer.

        Parameters
        ----------
        tags : data.Tag
            The tag to be encoded.

        Returns
        -------
        Optional[int]
            The encoded integer value representing the tag, or None if no
            encoding is available.
        """
        ...  # pragma: no cover

    def decode(self, index: int) -> data.Tag:
        """Decode an integer into a tag.

        Parameters
        ----------
        index : int
            The integer index to be decoded.

        Returns
        -------
        data.Tag
            The decoded tag.
        """
        ...  # pragma: no cover


class SimpleEncoder(Encoder):
    """A basic implementation of the Encoder protocol.

    This class provides a simple implementation of the Encoder protocol. It
    encodes tags into integers and decodes integers back into tags based on a
    provided list of tags.
    """

    def __init__(self, tags: Sequence[data.Tag]):
        """Initialize the SimpleEncoder with a list of tags.

        Parameters
        ----------
        tags : Sequence[data.Tag]
            A list of tags to be encoded.
        """
        self._tags = tags
        self._mapping = {
            (tag.term, tag.value): i for i, tag in enumerate(tags)
        }
        self.num_classes = len(tags)

    def encode(self, tag: data.Tag) -> Optional[int]:
        return self._mapping.get((tag.term, tag.value))

    def decode(self, index: int) -> data.Tag:
        return self._tags[index]


def create_tag_encoder(tags: Sequence[data.Tag]) -> SimpleEncoder:
    """Create an encoder object from a list of tags.

    Parameters
    ----------
    tags : Sequence[data.Tag]
        A list of tags to be encoded.

    Returns
    -------
    SimpleEncoder
        An instance of SimpleEncoder initialized with the provided tags.
    """
    return SimpleEncoder(tags)


def classification_encoding(
    tags: Sequence[data.Tag],
    encoder: Encoder,
) -> Optional[int]:
    """Encode a list of tags into an integer value.

    This function is commonly used for mapping a list of tags to a compact
    integer representation, typically representing classes associated with
    objects like clips or sound events.

    Parameters
    ----------
    tags : Sequence[data.Tag]
        A list of tags to be encoded.
    encoder : Callable[[data.Tag], Optional[int]]
        A callable object that takes a data.Tag object as input and returns
        an optional integer encoding. If the encoder returns None for a tag,
        it will be skipped.

    Returns
    -------
    encoded : Optional[int]
        The encoded integer value representing the tags, or None if no
        encoding is available.

    Examples
    --------
    Consider the following set of tags:

    >>> dog = data.Tag(key="animal", value="dog")
    >>> cat = data.Tag(key="animal", value="cat")
    >>> brown = data.Tag(key="color", value="brown")
    >>> blue = data.Tag(key="color", value="blue")

    If we are interested in encoding only the 'dog' and 'brown' classes, the
    following examples demonstrate how the encoding works for tag list:

    >>> encoder = create_tag_encoder([dog, brown])
    >>> classification_encoding([brown], encoder)
    1
    >>> classification_encoding([dog, blue], encoder)
    0
    >>> classification_encoding([dog, brown], encoder)
    0
    >>> classification_encoding([cat], encoder)
    None
    """
    for tag in tags:
        encoded = encoder.encode(tag)
        if encoded is not None:
            return encoded
    return None


def multilabel_encoding(
    tags: Sequence[data.Tag],
    encoder: Encoder,
) -> np.ndarray:
    """Encode a list of tags into a binary multilabel array.

    Parameters
    ----------
    tags
        A list of tags to be encoded.
    encoder
        A callable object that takes a data.Tag object as input and returns
        an optional integer encoding. If the encoder returns None for a tag,
        it will be skipped.

    Returns
    -------
    encoded : np.ndarray
        A binary numpy array of shape (num_classes,) representing the
        multilabel encoding for the input tags. Each index with a corresponding
        tag is set to 1, and the rest are 0.

    Examples
    --------
    Consider the following set of tags:

    >>> dog = data.Tag(key="animal", value="dog")
    >>> cat = data.Tag(key="animal", value="cat")
    >>> brown = data.Tag(key="color", value="brown")
    >>> blue = data.Tag(key="color", value="blue")

    And we are only interested in encoding the following two classes:

    >>> encoder = create_tag_encoder([dog, brown])

    Then the following examples show how the multilabel encoding works:

    >>> multilabel_encoding([brown], encoder)
    array([0, 1])
    >>> multilabel_encoding([dog, blue], encoder)
    array([1, 0])
    >>> multilabel_encoding([dog, brown], encoder)
    array([1, 1])
    >>> classification_encoding([cat], encoder)
    array([0, 0])
    """
    encoded = np.zeros(encoder.num_classes, dtype=np.int32)
    for tag in tags:
        index = encoder.encode(tag)
        if index is None:
            continue
        encoded[index] = 1
    return encoded


def prediction_encoding(
    tags: Sequence[data.PredictedTag],
    encoder: Encoder,
) -> np.ndarray:
    """Encode a list of predicted tags into a floating-point array of scores.

    Parameters
    ----------
    tags
        A list of predicted tags to be encoded.
    encoder
        A callable object that takes a data.Tag object as input and returns
        an optional integer encoding. If the encoder returns None for a tag,
        it will be skipped.

    Returns
    -------
    encoded : np.ndarray
        A numpy array of floats of shape (num_classes,) representing the
        predicted scores for each class. The array contains the scores for each
        class corresponding to the input predicted tags.

    Examples
    --------
    Consider the following set of tags:

    >>> dog = data.Tag(key="animal", value="dog")
    >>> cat = data.Tag(key="animal", value="cat")
    >>> brown = data.Tag(key="color", value="brown")
    >>> blue = data.Tag(key="color", value="blue")

    And we are only interested in encoding the following two classes:

    >>> encoder = create_tag_encoder([dog, brown])

    Then the following examples show how the encoding works for predicted tags:

    >>> prediction_encoding(
    ...     [data.PredictedTag(tag=brown, score=0.5)], encoder
    ... )
    array([0, 0.5])
    >>> multilabel_encoding(
    ...     [
    ...         data.PredictedTag(tag=dog, score=0.2),
    ...         data.PredictedTag(tag=blue, score=0.9),
    ...     ],
    ...     encoder,
    ... )
    array([0.2, 0])
    >>> multilabel_encoding(
    ...     [
    ...         data.PredictedTag(tag=dog, score=0.2),
    ...         data.PredictedTag(tag=brown, score=0.5),
    ...     ],
    ...     encoder,
    ... )
    array([0.2, 0.5])
    >>> classification_encoding(
    ...     [
    ...         data.PredictedTag(tag=cat, score=0.7),
    ...     ],
    ...     encoder,
    ... )
    array([0, 0])
    """
    encoded = np.zeros(encoder.num_classes, dtype=np.float32)
    for prediction in tags:
        index = encoder.encode(prediction.tag)
        if index is None:
            continue
        encoded[index] = prediction.score
    return encoded
