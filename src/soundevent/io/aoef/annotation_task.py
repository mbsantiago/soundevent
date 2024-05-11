import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from .adapters import DataAdapter
from .clip import ClipAdapter
from .user import UserAdapter
from soundevent import data


class StatusBadgeObject(BaseModel):
    """Schema definition for a status badge object in AOEF format."""

    state: data.AnnotationState
    owner: Optional[UUID] = None
    created_on: Optional[datetime.datetime] = None


class AnnotationTaskObject(BaseModel):
    """Schema definition for an annotation task object in AOEF format."""

    uuid: UUID
    clip: UUID
    status_badges: Optional[List[StatusBadgeObject]] = None
    created_on: Optional[datetime.datetime] = None


class AnnotationTaskAdapter(
    DataAdapter[data.AnnotationTask, AnnotationTaskObject, UUID, UUID]
):
    def __init__(
        self,
        clip_adapter: ClipAdapter,
        user_adapter: UserAdapter,
    ):
        super().__init__()
        self.clip_adapter = clip_adapter
        self.user_adapter = user_adapter

    def assemble_aoef(
        self,
        obj: data.AnnotationTask,
        obj_id: UUID,
    ) -> AnnotationTaskObject:
        for badge in obj.status_badges or []:
            if badge.owner is not None:
                self.user_adapter.to_aoef(badge.owner)

        return AnnotationTaskObject(
            uuid=obj.uuid,
            clip=self.clip_adapter.to_aoef(obj.clip).uuid,
            status_badges=(
                [
                    StatusBadgeObject(
                        state=badge.state,
                        owner=(
                            self.user_adapter.to_aoef(badge.owner).uuid
                            if badge.owner is not None
                            else None
                        ),
                        created_on=badge.created_on,
                    )
                    for badge in obj.status_badges
                ]
                if obj.status_badges
                else None
            ),
            created_on=obj.created_on,
        )

    def assemble_soundevent(
        self,
        obj: AnnotationTaskObject,
    ) -> data.AnnotationTask:
        clip = self.clip_adapter.from_id(obj.clip)

        if clip is None:
            raise ValueError(f"Clip with ID {obj.clip} not found.")

        return data.AnnotationTask(
            uuid=obj.uuid or uuid4(),
            clip=clip,
            status_badges=[
                data.StatusBadge(
                    state=badge.state,
                    owner=(
                        self.user_adapter.from_id(badge.owner)
                        if badge.owner is not None
                        else None
                    ),
                    created_on=badge.created_on or datetime.datetime.now(),
                )
                for badge in obj.status_badges or []
            ],
            created_on=obj.created_on or datetime.datetime.now(),
        )
