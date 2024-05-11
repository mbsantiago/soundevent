from typing import List, Literal, Optional

from .annotation_set import AnnotationSetAdapter, AnnotationSetObject
from soundevent import data


class EvaluationSetObject(AnnotationSetObject):
    """Schema definition for an evaluation set object in AOEF format."""

    collection_type: Literal["evaluation_set"] = "evaluation_set"  # type: ignore
    name: str
    description: Optional[str] = None
    evaluation_tags: Optional[List[int]] = None


class EvaluationSetAdapter(AnnotationSetAdapter):
    def to_aoef(  # type: ignore
        self,
        obj: data.EvaluationSet,  # type: ignore
    ) -> EvaluationSetObject:
        annotation_set = super().to_aoef(obj)
        return EvaluationSetObject(
            uuid=annotation_set.uuid,
            users=self.user_adapter.values(),
            tags=self.tag_adapter.values(),
            recordings=self.recording_adapter.values(),
            sound_events=self.sound_event_adapter.values(),
            sequences=self.sequence_adapter.values(),
            clips=self.clip_adapter.values(),
            sound_event_annotations=self.sound_event_annotations_adapter.values(),
            sequence_annotations=self.sequence_annotations_adapter.values(),
            clip_annotations=annotation_set.clip_annotations,
            created_on=obj.created_on,
            name=obj.name,
            description=obj.description,
            evaluation_tags=(
                [
                    self.tag_adapter.to_aoef(tag).id
                    for tag in obj.evaluation_tags
                ]
                if obj.evaluation_tags
                else None
            ),
        )

    def to_soundevent(  # type: ignore
        self,
        obj: EvaluationSetObject,  # type: ignore
    ) -> data.EvaluationSet:
        annotation_set = super().to_soundevent(obj)
        return data.EvaluationSet(
            **{
                field: value
                for field, value in annotation_set
                if value is not None
            },
            name=obj.name,
            description=obj.description,
            evaluation_tags=[
                tag
                for tag_id in obj.evaluation_tags or []
                if (tag := self.tag_adapter.from_id(tag_id)) is not None
            ],
        )
