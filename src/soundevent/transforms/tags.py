from collections.abc import Callable, Sequence
from typing import Optional

from soundevent import data
from soundevent.transforms.base import TransformBase

__all__ = [
    "TagsTransform",
]


class TagsTransform(TransformBase):
    def __init__(
        self, transform: Callable[[Sequence[data.Tag]], Sequence[data.Tag]]
    ):
        self.transform = transform

    def transform_tags(self, tags: Sequence[data.Tag]) -> Sequence[data.Tag]:
        return self.transform(tags)

    @classmethod
    def from_tag_transform(
        cls,
        transform: Callable[[data.Tag], Optional[data.Tag]],
    ):
        def tags_transform(tags: Sequence[data.Tag]) -> Sequence[data.Tag]:
            ret = []

            for tag in tags:
                transformed = transform(tag)

                if transformed is None:
                    continue

                ret.append(transformed)

            return ret

        return cls(tags_transform)
