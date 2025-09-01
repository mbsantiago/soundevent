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
    >>> from soundevent import data
    >>> from soundevent.transforms import TagsTransform
    >>>
    >>> # Assume `dataset` is a soundevent Dataset object
    >>> # Example 1: Remove a specific tag using a sequence transform
    >>> def remove_tag(tags: Sequence[data.Tag]) -> list[data.Tag]:
    ...     return [tag for tag in tags if tag.key != "unwanted_tag"]
    ...
    >>> remover = TagsTransform(transform=remove_tag)
    >>> transformed_dataset = remover.transform_dataset(dataset)
    >>>
    >>> # Example 2: Using the factory to rename a tag
    >>> def rename_tag(tag: data.Tag) -> data.Tag:
    ...     if tag.key == "old_name":
    ...         return tag.model_copy(update={"key": "new_name"})
    ...     return tag
    ...
    >>> renamer = TagsTransform.from_tag_transform(transform=rename_tag)
    >>> transformed_dataset_2 = renamer.transform_dataset(dataset)

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