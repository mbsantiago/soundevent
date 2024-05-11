from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from pydantic import BaseModel

from .adapters import DataAdapter
from .sound_event import SoundEventAdapter
from .tag import TagAdapter
from soundevent import data


class SoundEventPredictionObject(BaseModel):
    uuid: UUID
    sound_event: UUID
    score: float
    tags: Optional[List[Tuple[int, float]]] = None


class SoundEventPredictionAdapter(
    DataAdapter[
        data.SoundEventPrediction, SoundEventPredictionObject, UUID, UUID
    ]
):
    def __init__(
        self,
        sound_event_adapter: SoundEventAdapter,
        tag_adapter: TagAdapter,
    ):
        super().__init__()
        self.sound_event_adapter = sound_event_adapter
        self.tag_adapter = tag_adapter

    def assemble_aoef(
        self,
        obj: data.SoundEventPrediction,
        obj_id: UUID,
    ) -> SoundEventPredictionObject:
        return SoundEventPredictionObject(
            sound_event=self.sound_event_adapter.to_aoef(obj.sound_event).uuid,
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
        obj: SoundEventPredictionObject,
    ) -> data.SoundEventPrediction:
        sound_event = self.sound_event_adapter.from_id(obj.sound_event)

        if sound_event is None:
            raise ValueError(
                f"Sound event with ID {obj.sound_event} not found."
            )

        return data.SoundEventPrediction(
            uuid=obj.uuid or uuid4(),
            sound_event=sound_event,
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
