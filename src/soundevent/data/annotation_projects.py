"""Annotation Project Management.

This module defines the `AnnotationProject` class, which represents a complete
annotation project. It organizes the entire workflow, including the audio clips
to be annotated (via tasks), the annotations produced, guidelines for
annotators, and the set of permissible tags. It serves as a central container
for managing and tracking the progress of an annotation effort.
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
    """Represents an annotation project.

    An `AnnotationProject` extends an `AnnotationSet` by adding
    project-specific details necessary for organizing and carrying out an
    annotation task. It includes the set of clips to be annotated
    (defined within `AnnotationTask` objects), instructions for the annotators,
    and the official list of tags that can be used within the project.

    It inherits from `AnnotationSet` and adds structure for tracking the
    annotation process itself.

    Attributes
    ----------
    instructions
        Optional textual instructions for annotators working on this project.
    annotation_tags
        A list of `Tag` objects that are permitted for use in annotations
        within this project.
    tasks
        A list of `AnnotationTask` objects, each defining a specific clip
        that requires annotation as part of this project.
    """

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
