from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from pydantic import BaseModel

from .adapters import DataAdapter
from .sequence import SequenceAdapter
from .tag import TagAdapter
from soundevent import data


class SequencePredictionObject(BaseModel):
    uuid: UUID
    sequence: UUID
    score: float
    tags: Optional[List[Tuple[int, float]]] = None


class SequencePredictionAdapter(
    DataAdapter[data.SequencePrediction, SequencePredictionObject, UUID, UUID]
):
    def __init__(
        self,
        sequence_adapter: SequenceAdapter,
        tag_adapter: TagAdapter,
    ):
        super().__init__()
        self.sequence_adapter = sequence_adapter
        self.tag_adapter = tag_adapter

    def assemble_aoef(
        self,
        obj: data.SequencePrediction,
        obj_id: UUID,
    ) -> SequencePredictionObject:
        return SequencePredictionObject(
            sequence=self.sequence_adapter.to_aoef(obj.sequence).uuid,
            uuid=obj.uuid,
            score=obj.score,
            tags=(
                [
                    (tag.id, predicted_tag.score)
                    for predicted_tag in obj.tags
                    if (tag := self.tag_adapter.to_aoef(predicted_tag.tag))
                    is not None
                ]
                if obj.tags
                else None
            ),
        )

    def assemble_soundevent(
        self,
        obj: SequencePredictionObject,
    ) -> data.SequencePrediction:
        sequence = self.sequence_adapter.from_id(obj.sequence)

        if sequence is None:
            raise ValueError(f"Sequence with ID {obj.sequence} not found.")

        return data.SequencePrediction(
            uuid=obj.uuid or uuid4(),
            sequence=sequence,
            score=obj.score,
            tags=[
                data.PredictedTag(
                    tag=tag,
                    score=score,
                )
                for tag_id, score in obj.tags or []
                if (tag := self.tag_adapter.from_id(tag_id)) is not None
            ],
        )
