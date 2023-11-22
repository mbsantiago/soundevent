import sys
from abc import ABC, abstractmethod
from typing import Dict, Generic, Hashable, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel

from soundevent import data
from soundevent.io.types import DataObject

if sys.version_info < (3, 8):
    from typing_extensions import Protocol  # pragma: no cover
else:
    from typing import Protocol


__all__ = [
    "AdapterProtocol",
    "DataAdapter",
]


class HasUUID(Protocol):
    uuid: UUID


class HasID(Protocol):
    id: int


A = TypeVar("A", bound=HasUUID)
B = TypeVar("B", bound=HasID)
C = TypeVar("C", bound=DataObject)
D = TypeVar("D", bound=BaseModel)


class AdapterProtocol(Protocol, Generic[C, D]):
    def __init__(
        self,
        audio_dir: Optional[data.PathLike] = None,
    ):
        ...

    def to_aoef(self, obj: C) -> D:
        ...

    def to_soundevent(self, obj: D) -> C:
        ...


class DataAdapter(ABC, Generic[A, B]):
    """Base class for data adapters.

    A data adapter is used to convert between sound event and AOEF data
    types.

    For storage efficiency reasons, AOEF data types use integer IDs to
    reference other objects. This class provides a mapping between the
    integer IDs and the objects themselves.
    """

    def __init__(self):
        self._mapping: Dict[Hashable, int] = {}
        self._soundevent_store: Dict[int, A] = {}
        self._aoef_store: Dict[int, B] = {}

    @abstractmethod
    def assemble_aoef(self, obj: A, obj_id: int) -> B:
        """Create AOEF object from sound event object.

        Parameters
        ----------
        obj
            Sound event object.
        obj_id
            The provided ID for the object in the AOEF format.
            The user does not have to worry about generating
            this ID. The data adapter will take care of it.
        """
        ...

    @abstractmethod
    def assemble_soundevent(self, obj: B) -> A:
        """Create sound event object from AOEF object."""
        ...

    @classmethod
    def _get_key(cls, obj: A) -> Hashable:
        """Get key for object.

        Internally, the data adapter uses a mapping between objects and
        IDs. This method returns the key used for the mapping.
        """
        return obj.uuid

    def to_aoef(self, obj: A) -> B:
        """Convert object to AOEF format."""
        obj_id = self.get_id(obj)

        if obj_id not in self._aoef_store:
            aoef_obj = self.assemble_aoef(obj, obj_id)
            self._aoef_store[obj_id] = aoef_obj

        if obj_id not in self._soundevent_store:
            self._soundevent_store[obj_id] = obj

        return self._aoef_store[obj_id]

    def to_soundevent(self, obj: B) -> A:
        """Convert object to sound event format."""
        obj_id = obj.id

        if obj_id not in self._soundevent_store:
            soundevent_obj = self.assemble_soundevent(obj)
            self._soundevent_store[obj_id] = soundevent_obj

        if obj_id not in self._aoef_store:
            self._aoef_store[obj_id] = obj

        return self._soundevent_store[obj_id]

    def from_id(self, obj_id: int) -> Optional[A]:
        """Get object from ID."""
        return self._soundevent_store.get(obj_id)

    def get_id(self, obj: A) -> int:
        """Get ID for object."""
        key = self._get_key(obj)

        if key not in self._mapping:
            obj_id = len(self._mapping)
            self._mapping[key] = obj_id

        obj_id = self._mapping[key]

        if obj_id not in self._soundevent_store:
            self._soundevent_store[obj_id] = obj

        return obj_id

    def values(self) -> Optional[List[B]]:
        """Get all registered objects."""
        if not self._aoef_store:
            return None
        return list(self._aoef_store.values())
