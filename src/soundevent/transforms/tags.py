"""Transformations for tags."""

from collections.abc import Callable, Sequence
from typing import Optional

from soundevent import data
from soundevent.transforms.base import TransformBase

__all__ = [
    "TagsTransform",
]


class TagsTransform(TransformBase):
    """A transform for modifying sequences of tags.

    This class provides a way to apply a transformation to all `Tag`
    sequences within a soundevent data structure. It is useful for
    filtering, renaming, or otherwise modifying tags across an entire
    dataset.

    It can be initialized directly with a function that transforms a whole
    sequence of tags, or it can be constructed from a function that transforms
    a single tag using the `from_tag_transform` class method.

    Parameters
    ----------
    transform : Callable[[Sequence[data.Tag]], Sequence[data.Tag]]
        A function that takes a sequence of `Tag` objects and returns a
        transformed sequence of `Tag` objects.

    Examples
    --------
    >>> from pathlib import Path
    >>> from soundevent import data
    >>> from soundevent.transforms import TagsTransform
    >>>
    >>> # Create a sample recording with a misspelled species tag
    >>> recording = data.Recording(
    ...     path=Path("rec.wav"),
    ...     duration=1,
    ...     channels=1,
    ...     samplerate=16000,
    ...     tags=[
    ...         data.Tag(key="species", value="Myotis mytis"),
    ...         data.Tag(key="quality", value="good"),
    ...     ],
    ... )
    >>>
    >>> # Create a transform to correct the spelling of "Myotis myotis"
    >>> def correct_species_name(tag: data.Tag) -> data.Tag:
    ...     if tag.key == "species" and tag.value == "Myotis mytis":
    ...         return tag.model_copy(update={"value": "Myotis myotis"})
    ...     return tag
    >>> corrector = TagsTransform.from_tag_transform(
    ...     transform=correct_species_name
    ... )
    >>> transformed_recording = corrector.transform_recording(recording)
    >>>
    >>> # Verify that the tag value has been corrected
    >>> species_tag = next(
    ...     t for t in transformed_recording.tags if t.key == "species"
    ... )
    >>> species_tag.value
    'Myotis myotis'
    >>>
    >>> # Verify that other tags are untouched
    >>> quality_tag = next(
    ...     t for t in transformed_recording.tags if t.key == "quality"
    ... )
    >>> quality_tag.value
    'good'

    """

    def __init__(
        self, transform: Callable[[Sequence[data.Tag]], Sequence[data.Tag]]
    ):
        """Initialize the TagsTransform.

        Parameters
        ----------
        transform : Callable[[Sequence[data.Tag]], Sequence[data.Tag]]
            A function that takes a sequence of `Tag` objects and returns a
            transformed sequence of `Tag` objects.
        """
        self.transform = transform

    def transform_tags(self, tags: Sequence[data.Tag]) -> Sequence[data.Tag]:
        """Apply the transformation to a sequence of tags.

        Parameters
        ----------
        tags : Sequence[data.Tag]
            The sequence of tags to transform.

        Returns
        -------
        Sequence[data.Tag]
            The transformed sequence of tags.
        """
        return self.transform(tags)

    @classmethod
    def from_tag_transform(
        cls,
        transform: Callable[[data.Tag], Optional[data.Tag]],
    ):
        """Create a TagsTransform from a function that transforms a single tag.

        This factory method is a convenient way to create a `TagsTransform`
        when your logic applies to each tag individually.

        Parameters
        ----------
        transform : Callable[[data.Tag], Optional[data.Tag]]
            A function that takes a single `Tag` object and returns either a
            transformed `Tag` object or `None`. If `None` is returned, the
            tag is removed from the sequence.

        Returns
        -------
        TagsTransform
            A new `TagsTransform` instance.
        """

        def tags_transform(tags: Sequence[data.Tag]) -> Sequence[data.Tag]:
            ret = []

            for tag in tags:
                transformed = transform(tag)

                if transformed is None:
                    continue

                ret.append(transformed)

            return ret

        return cls(tags_transform)
