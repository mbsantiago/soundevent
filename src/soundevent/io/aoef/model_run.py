from typing import Literal, Optional

from .prediction_set import PredictionSetAdapter, PredictionSetObject
from soundevent import data


class ModelRunObject(PredictionSetObject):
    collection_type: Literal["model_run"] = "model_run"  # type: ignore
    name: str
    version: Optional[str] = None
    description: Optional[str] = None


class ModelRunAdapter(PredictionSetAdapter):
    def to_aoef(self, obj: data.ModelRun) -> ModelRunObject:  # type: ignore
        prediction_set = super().to_aoef(obj)
        return ModelRunObject(
            uuid=prediction_set.uuid,
            created_on=prediction_set.created_on,
            users=self.user_adapter.values(),
            tags=self.tag_adapter.values(),
            recordings=self.recording_adapter.values(),
            sound_events=self.sound_event_adapter.values(),
            sequences=self.sequence_adapter.values(),
            clips=self.clip_adapter.values(),
            sound_event_predictions=self.sound_event_prediction_adapter.values(),
            sequence_predictions=self.sequence_prediction_adapter.values(),
            clip_predictions=prediction_set.clip_predictions,
            name=obj.name,
            version=obj.version,
            description=obj.description,
        )

    def to_soundevent(self, obj: ModelRunObject) -> data.ModelRun:  # type: ignore
        prediction_set = super().to_soundevent(obj)
        return data.ModelRun(
            **dict(prediction_set),
            name=obj.name,
            version=obj.version,
            description=obj.description,
        )
