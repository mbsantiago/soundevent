import sys
from abc import ABC, abstractmethod
from typing import Dict, Generic, Hashable, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel

from soundevent import data
from soundevent.io.types import DataCollections

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


SoundEventObject = TypeVar("SoundEventObject", bound=HasUUID)
AOEFObject = TypeVar("AOEFObject", bound=HasUUID)
SoundEventKey = TypeVar("SoundEventKey", bound=Hashable)
AOEFKey = TypeVar("AOEFKey", bound=Hashable)
C = TypeVar("C", bound=DataCollections)
D = TypeVar("D", bound=BaseModel)


class AdapterProtocol(Protocol, Generic[C, D]):
    def __init__(
        self,
        audio_dir: Optional[data.PathLike] = None,
    ): ...

    def to_aoef(self, obj: C) -> D: ...

    def to_soundevent(self, obj: D) -> C: ...


class DataAdapter(
    ABC, Generic[SoundEventObject, AOEFObject, SoundEventKey, AOEFKey]
):
    """Base class for data adapters.

    A data adapter is used to convert between sound event and AOEF data
    types.

    For storage efficiency reasons, AOEF data types use integer IDs to
    reference other objects. This class provides a mapping between the
    integer IDs and the objects themselves.
    """

    def __init__(self):
        self._mapping: Dict[SoundEventKey, AOEFKey] = {}
        self._soundevent_store: Dict[AOEFKey, SoundEventObject] = {}
        self._aoef_store: Dict[AOEFKey, AOEFObject] = {}

    @abstractmethod
    def assemble_aoef(
        self, obj: SoundEventObject, obj_id: AOEFKey
    ) -> AOEFObject:
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
    def assemble_soundevent(self, obj: AOEFObject) -> SoundEventObject:
        """Create sound event object from AOEF object."""
        ...

    @classmethod
    def _get_soundevent_key(cls, obj: SoundEventObject) -> SoundEventKey:
        """Get key for object.

        Internally, the data adapter uses a mapping between objects and
        IDs. This method returns the key used for the mapping.
        """
        return obj.uuid  # type: ignore

    @classmethod
    def _get_aoef_key(cls, obj: AOEFObject) -> AOEFKey:
        """Get key for object.

        Internally, the data adapter uses a mapping between objects and
        IDs. This method returns the key used for the mapping.
        """
        return obj.uuid  # type: ignore

    def to_aoef(self, obj: SoundEventObject) -> AOEFObject:
        """Convert object to AOEF format."""
        obj_id = self.get_id(obj)

        if obj_id not in self._aoef_store:
            aoef_obj = self.assemble_aoef(obj, obj_id)
            self._aoef_store[obj_id] = aoef_obj

        if obj_id not in self._soundevent_store:
            self._soundevent_store[obj_id] = obj

        return self._aoef_store[obj_id]

    def to_soundevent(self, obj: AOEFObject) -> SoundEventObject:
        """Convert object to sound event format."""
        obj_id = self._get_aoef_key(obj)

        if obj_id not in self._soundevent_store:
            soundevent_obj = self.assemble_soundevent(obj)
            self._soundevent_store[obj_id] = soundevent_obj

        if obj_id not in self._aoef_store:
            self._aoef_store[obj_id] = obj

        return self._soundevent_store[obj_id]

    def from_id(self, obj_id: AOEFKey) -> Optional[SoundEventObject]:
        """Get object from ID."""
        return self._soundevent_store.get(obj_id)

    def get_new_id(self, obj: SoundEventObject) -> AOEFKey:
        """Get new ID for object."""
        return obj.uuid  # type: ignore

    def get_id(self, obj: SoundEventObject) -> AOEFKey:
        """Get ID for object."""
        key = self._get_soundevent_key(obj)

        if key not in self._mapping:
            obj_id = self.get_new_id(obj)
            self._mapping[key] = obj_id

        obj_id = self._mapping[key]

        if obj_id not in self._soundevent_store:
            self._soundevent_store[obj_id] = obj

        return obj_id

    def values(self) -> Optional[List[AOEFObject]]:
        """Get all registered objects."""
        if not self._aoef_store:
            return None
        return list(self._aoef_store.values())
