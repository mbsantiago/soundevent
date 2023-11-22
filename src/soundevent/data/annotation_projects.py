"""Annotation Project.

This module defines the `AnnotationProject` class, which represents a project
comprising a set of audio clips that need to be annotated. Each project has a
name, a description of the annotation goals, instructions for annotators, and a
set of tags to be used during annotation work. The project also tracks
annotated clips and ensures they are part of the project.
"""

from typing import List, Optional

from pydantic import Field, model_validator

from soundevent.data.annotation_sets import AnnotationSet
from soundevent.data.annotation_tasks import AnnotationTask
from soundevent.data.tags import Tag

__all__ = [
    "AnnotationProject",
]


class AnnotationProject(AnnotationSet):
    """Annotation Project Class."""

    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    annotation_tags: List[Tag] = Field(default_factory=list, repr=False)
    tasks: List[AnnotationTask] = Field(default_factory=list, repr=False)

    @model_validator(mode="after")
    def _annotations_are_part_of_the_project(self):
        """Ensure annotated clips are part of the project."""
        clip_ids = {task.clip.uuid for task in self.tasks}

        for annotated_clip in self.clip_annotations:
            if annotated_clip.clip.uuid not in clip_ids:
                raise ValueError(
                    f"Annotated clip {annotated_clip.uuid} is not part "
                    "of the project"
                )

        return self
