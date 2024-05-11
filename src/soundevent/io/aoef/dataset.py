from typing import Literal, Optional

from .recording_set import RecordingSetAdapter, RecordingSetObject
from soundevent import data


class DatasetObject(RecordingSetObject):
    """Schema definition for a dataset object in AOEF format."""

    collection_type: Literal["dataset"] = "dataset"  # type: ignore
    name: str
    description: Optional[str] = None


class DatasetAdapter(RecordingSetAdapter):
    def to_aoef(  # type: ignore
        self,
        obj: data.Dataset,  # type: ignore
    ) -> DatasetObject:
        recording_set = super().to_aoef(obj)
        return DatasetObject(
            **{
                key: value
                for key, value in recording_set
                if value is not None and key != "collection_type"
            },
            name=obj.name,
            description=obj.description,
        )

    def to_soundevent(  # type: ignore
        self,
        obj: DatasetObject,  # type: ignore
    ) -> data.Dataset:
        recording_set = super().to_soundevent(obj)
        return data.Dataset(
            **{
                key: value for key, value in recording_set if value is not None
            },
            name=obj.name,
            description=obj.description,
        )
