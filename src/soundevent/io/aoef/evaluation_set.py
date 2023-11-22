from typing import List, Literal, Optional

from soundevent import data

from .annotation_set import AnnotationSetAdapter, AnnotationSetObject


class EvaluationSetObject(AnnotationSetObject):
    """Schema definition for an evaluation set object in AOEF format."""

    collection_type: Literal["evaluation_set"] = "evaluation_set"
    name: str
    description: Optional[str] = None
    evaluation_tags: Optional[List[int]] = None


class EvaluationSetAdapter(AnnotationSetAdapter):
    def to_aoef(self, obj: data.EvaluationSet) -> EvaluationSetObject:
        annotation_set = super().to_aoef(obj)
        return EvaluationSetObject(
            **dict(annotation_set),
            name=obj.name,
            description=obj.description,
            evaluation_tags=[
                self.tag_adapter.to_aoef(tag).id for tag in obj.evaluation_tags
            ]
            if obj.evaluation_tags
            else None,
        )

    def to_soundevent(self, obj: EvaluationSetObject) -> data.EvaluationSet:
        annotation_set = super().to_soundevent(obj)
        return data.EvaluationSet(
            **dict(annotation_set),
            name=obj.name,
            description=obj.description,
            evaluation_tags=[
                tag
                for tag_id in obj.evaluation_tags or []
                if (tag := self.tag_adapter.from_id(tag_id)) is not None
            ],
        )