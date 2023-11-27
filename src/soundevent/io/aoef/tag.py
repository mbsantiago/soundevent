from typing import Tuple

from pydantic import BaseModel

from soundevent import data

from .adapters import DataAdapter

__all__ = ["TagObject"]


class TagObject(BaseModel):
    """Schema definition for a tag object in AOEF format."""

    id: int
    key: str
    value: str


class TagAdapter(DataAdapter[data.Tag, TagObject]):  # type: ignore
    def assemble_aoef(self, obj: data.Tag, obj_id: int) -> TagObject:
        return TagObject(
            id=obj_id,
            key=obj.key,
            value=obj.value,
        )

    def assemble_soundevent(self, obj: TagObject) -> data.Tag:
        return data.Tag(
            key=obj.key,
            value=obj.value,
        )

    @classmethod
    def _get_soundevent_key(cls, tag: data.Tag) -> Tuple[str, str]:
        return (tag.key, tag.value)

    @classmethod
    def _get_aoef_key(cls, tag: TagObject) -> int:
        return tag.id

    def get_new_id(self, _: TagObject) -> int:
        """Get new ID for object."""
        return len(self._mapping)
