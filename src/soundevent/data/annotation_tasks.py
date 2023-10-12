"""Annotation Tasks.

Annotation tasks form a fundamental component of annotation projects
in bioacoustic research. The `soundevent` package introduces the
`AnnotationTask` class, which represents a unit of annotation work. An
annotation task corresponds to a specific recording clip that requires
thorough annotation based on provided instructions.

## Composition and Annotation Instructions

Each annotation task is composed of a distinct recording clip that
serves as the focus of annotation. Annotators are tasked with
meticulously annotating the clip according to the given annotation
instructions. These instructions serve as a guide, directing
annotators to identify and describe sound events within the clip,
capture relevant acoustic content, and include any pertinent
contextual tags.

## Annotator-Provided Tags and Annotations

Annotations allow annotators to contribute their expertise and
insights by including tags that describe the acoustic content of the
entire audio clip. These annotator-provided tags offer valuable
semantic information, enhancing the overall understanding of the audio
material. Additionally, annotators identify and annotate specific
sound events within the task clip, contributing to the detailed
analysis and characterization of the audio data.

## Notes and Completion Status

Annotations can be further enriched by including notes, enabling
annotators to provide additional discussions, explanations, or details
related to the annotation task. Once an annotation task is completed,
it can be marked as such. In multi-annotator scenarios, registering
the user who completed the task allows for tracking and
accountability.

## Functionality and Management

The `AnnotationTask` class provides essential functionality to manage
and track the progress of annotation tasks within an annotation
project. It empowers researchers to handle individual annotation
tasks, extract relevant information, and perform analyses based on the
completed annotations. Utilizing the `AnnotationTask` class facilitates
effective management and processing of annotation tasks, ultimately
enabling comprehensive analysis of audio recordings in bioacoustic
research projects.
"""
import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.annotations import Annotation
from soundevent.data.clips import Clip
from soundevent.data.notes import Note
from soundevent.data.tags import Tag

__all__ = [
    "AnnotationTask",
    "TaskState",
    "StatusBadge",
]


class TaskState(str, Enum):
    """Task State Enumeration.

    The TaskState enum represents the different states an annotation task can
    be in during its lifecycle. These states provide clear insights into the
    progress of the annotation process, helping users understand the current
    stage of the task.

    Attributes
    ----------
    assigned
        The task has been assigned to an annotator for completion.
    completed
        The task has been successfully completed by the annotator.
    verified
        The completed task has been reviewed and verified by a designated
        reviewer.
    rejected
        The task has been reviewed and rejected by the reviewer, indicating
        issues that need to be addressed.
    """

    assigned = "assigned"
    completed = "completed"
    verified = "verified"
    rejected = "rejected"


class StatusBadge(BaseModel):
    """Annotation Status Badge Class.

    The StatusBadge class represents an indicator of the current state of an
    annotation task. It includes information such as the task state, the
    responsible user, and the creation timestamp.

    Attributes
    ----------
    state
        The TaskState enum indicating the current state of the annotation task.
    user
        Optional field specifying the user responsible for this status badge.
    created_at
        The date and time when the status badge was created, providing a
        historical record of the badge's creation time.
    """

    state: TaskState
    user: Optional[str] = None
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )


class AnnotationTask(BaseModel):
    """Annotation Task Class.

    The AnnotationTask class encapsulates the essential components of an
    annotation task in the context of bioacoustic research. Annotation tasks
    are fundamental to the process of analyzing audio clips, as they involve
    annotators marking sound events, adding notes, and attaching tags for
    further interpretation.

    Attributes
    ----------
    uuid
        A unique identifier for the annotation task, ensuring traceability and
        uniqueness.
    clip
        The audio clip being annotated, providing the context for the
        annotations.
    annotations
        A list of Annotation objects, representing the marked sound events
        within the annotated clip. These annotations serve as the primary
        output of the annotation task.
    notes : List[Note]
        A list of Note objects, containing additional textual information and
        context provided by annotators during the annotation process.
    tags
        A list of Tag objects, reflecting user-provided labels or categories
        associated with the annotated clip. Tags offer a high-level overview of
        the content.
    status_badges
        A list of StatusBadge objects, indicating the current status or
        progress of the annotation task, such as completion or pending review.
    """

    uuid: UUID = Field(default_factory=uuid4)
    clip: Clip
    annotations: List[Annotation] = Field(default_factory=list)
    notes: List[Note] = Field(default_factory=list)
    tags: List[Tag] = Field(default_factory=list)
    status_badges: List[StatusBadge] = Field(default_factory=list)

    def __hash__(self):
        """Compute the hash value for the annotation task."""
        return hash(self.uuid)
