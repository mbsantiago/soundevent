from typing import Dict, List, Optional, Tuple
from uuid import UUID

from pydantic import BaseModel

from .adapters import DataAdapter
from .clip import ClipAdapter
from .sequence_prediction import SequencePredictionAdapter
from .sound_event_prediction import SoundEventPredictionAdapter
from .tag import TagAdapter
from soundevent import data


class ClipPredictionsObject(BaseModel):
    uuid: UUID
    clip: UUID
    sound_events: Optional[List[UUID]] = None
    sequences: Optional[List[UUID]] = None
    tags: Optional[List[Tuple[int, float]]] = None
    features: Optional[Dict[str, float]] = None


class ClipPredictionsAdapter(
    DataAdapter[data.ClipPrediction, ClipPredictionsObject, UUID, UUID]
):
    def __init__(
        self,
        clip_adapter: ClipAdapter,
        sound_event_prediction_adapter: SoundEventPredictionAdapter,
        tag_adapter: TagAdapter,
        sequence_prediction_adapter: SequencePredictionAdapter,
    ):
        super().__init__()
        self.clip_adapter = clip_adapter
        self.sound_event_prediction_adapter = sound_event_prediction_adapter
        self.tag_adapter = tag_adapter
        self.sequence_prediction_adapter = sequence_prediction_adapter

    def assemble_aoef(
        self,
        obj: data.ClipPrediction,
        obj_id: UUID,
    ) -> ClipPredictionsObject:
        return ClipPredictionsObject(
            uuid=obj.uuid,
            clip=self.clip_adapter.to_aoef(obj.clip).uuid,
            sound_events=(
                [
                    self.sound_event_prediction_adapter.to_aoef(
                        sound_event
                    ).uuid
                    for sound_event in obj.sound_events
                ]
                if obj.sound_events
                else None
            ),
            sequences=(
                [
                    self.sequence_prediction_adapter.to_aoef(sequence).uuid
                    for sequence in obj.sequences
                ]
                if obj.sequences
                else None
            ),
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
            features=(
                {
                    data.key_from_term(feature.term): feature.value
                    for feature in obj.features
                }
                if obj.features is not None
                else None
            ),
        )

    def assemble_soundevent(
        self,
        obj: ClipPredictionsObject,
    ) -> data.ClipPrediction:
        clip = self.clip_adapter.from_id(obj.clip)

        if clip is None:
            raise ValueError(f"Clip with ID {obj.clip} not found.")

        return data.ClipPrediction(
            uuid=obj.uuid,
            clip=clip,
            sound_events=[
                se_pred
                for sound_event in obj.sound_events or []
                if (
                    se_pred := self.sound_event_prediction_adapter.from_id(
                        sound_event
                    )
                )
                is not None
            ],
            sequences=[
                seq_pred
                for sequence in obj.sequences or []
                if (
                    seq_pred := self.sequence_prediction_adapter.from_id(
                        sequence
                    )
                )
                is not None
            ],
            tags=[
                data.PredictedTag(
                    tag=tag,
                    score=score,
                )
                for tag_id, score in obj.tags or {}
                if (tag := self.tag_adapter.from_id(tag_id)) is not None
            ],
            features=[
                data.Feature(term=data.term_from_key(name), value=value)
                for name, value in (obj.features or {}).items()
            ],
        )
