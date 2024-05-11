from typing import List, Literal, Optional

from .annotation_set import AnnotationSetAdapter, AnnotationSetObject
from .annotation_task import AnnotationTaskAdapter, AnnotationTaskObject
from soundevent import data

ColType = Literal["annotation_project"]


class AnnotationProjectObject(AnnotationSetObject):
    """Schema definition for an annotation project object in AOEF format."""

    collection_type: ColType = "annotation_project"  # type: ignore
    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    project_tags: Optional[List[int]] = None
    tasks: Optional[List[AnnotationTaskObject]] = None


class AnnotationProjectAdapter(AnnotationSetAdapter):
    def __init__(
        self,
        annotation_task_adapter: Optional[AnnotationTaskAdapter] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.annotation_task_adapter = (
            annotation_task_adapter
            or AnnotationTaskAdapter(
                self.clip_adapter,
                self.user_adapter,
            )
        )

    def to_aoef(  # type: ignore
        self,
        obj: data.AnnotationProject,  # type: ignore
    ) -> AnnotationProjectObject:
        tasks = [
            self.annotation_task_adapter.to_aoef(task)
            for task in obj.tasks or []
        ]

        project_tags = [
            self.tag_adapter.to_aoef(tag).id for tag in obj.annotation_tags
        ]

        annotation_set = super().to_aoef(obj)

        return AnnotationProjectObject(
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
            instructions=obj.instructions,
            project_tags=project_tags if project_tags else None,
            tasks=tasks,
        )

    def to_soundevent(  # type: ignore
        self,
        obj: AnnotationProjectObject,  # type: ignore
    ) -> data.AnnotationProject:
        annotation_set = super().to_soundevent(obj)

        tasks = [
            self.annotation_task_adapter.to_soundevent(task)
            for task in obj.tasks or []
        ]

        return data.AnnotationProject(
            **{
                field: value
                for field, value in annotation_set
                if value is not None
            },
            tasks=tasks,
            name=obj.name,
            description=obj.description,
            instructions=obj.instructions,
            annotation_tags=[
                tag
                for tag_id in (obj.project_tags or [])
                if (tag := self.tag_adapter.from_id(tag_id)) is not None
            ],
        )
