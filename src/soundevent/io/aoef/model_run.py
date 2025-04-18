import warnings
from typing import Any, Literal, Optional

from pydantic import BaseModel, computed_field, model_validator

from .prediction_set import PredictionSetAdapter, PredictionSetObject
from soundevent import data


class ModelInfoObject(BaseModel):
    name: str
    version: Optional[str] = None
    description: Optional[str] = None


class ModelRunObject(PredictionSetObject):
    collection_type: Literal["model_run"] = "model_run"  # type: ignore
    model: Optional[ModelInfoObject] = None

    @computed_field
    @property
    def version(self) -> Optional[str]:
        """Provides backward-compatible access to 'version'. Deprecated."""
        warnings.warn(
            "Accessing 'version' directly on ModelRun is deprecated. "
            "Use 'model_run.model.version' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if self.model is None:
            return None

        return self.model.version

    @version.setter
    def version(self, value: str) -> None:
        warnings.warn(
            "Setting 'version' directly on ModelRun is deprecated. "
            "Set 'model_run.model.version' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if self.model is None:
            raise ValueError("ModelRun object has no model attribute.")

        self.model.version = value

    @model_validator(mode="before")
    @classmethod
    def _fill_in_missing_model_info(cls, data: Any) -> Any:
        """Transform old flat input data to the new nested structure."""
        if not isinstance(data, dict):
            return data

        if "model" in data:
            return data

        old_keys = {"version"}
        if old_keys.issubset(data.keys()):
            warnings.warn(
                "Initializing ModelRunObject with ('version',) is deprecated. "
                "Provide data in the nested format: "
                "{'model': {'model_info': {'name':..., 'description':...}, 'version':...}}",
                DeprecationWarning,
                stacklevel=3,
            )

            return {
                **data,
                "model": {
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "version": data.get("version"),
                },
            }

        return data


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
            name=obj.name or "Model Run",
            description=obj.description,
            model=ModelInfoObject(
                name=obj.model.info.name,
                version=obj.model.version,
                description=obj.model.info.description,
            ),
        )

    def to_soundevent(self, obj: ModelRunObject) -> data.ModelRun:  # type: ignore
        prediction_set = super().to_soundevent(obj)
        model_info = (
            {
                "info": {
                    "name": obj.model.name,
                    "description": obj.model.description,
                },
                "version": obj.model.version,
            }
            if obj.model is not None
            else {}
        )
        return data.ModelRun.model_validate(
            {
                **dict(prediction_set),
                "name": obj.name,
                "version": obj.version,
                "description": obj.description,
                "model": model_info,
            },
        )
