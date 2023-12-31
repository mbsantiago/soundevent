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


class TagAdapter(DataAdapter[data.Tag, TagObject, Tuple[str, str], int]):  # type: ignore
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
    def _get_soundevent_key(cls, obj: data.Tag) -> Tuple[str, str]:
        return (obj.key, obj.value)

    @classmethod
    def _get_aoef_key(cls, obj: TagObject) -> int:
        return obj.id

    def get_new_id(self, obj: data.Tag) -> int:
        """Get new ID for object."""
        return len(self._mapping)
