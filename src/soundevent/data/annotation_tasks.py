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
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.annotations import Annotation
from soundevent.data.clips import Clip
from soundevent.data.notes import Note
from soundevent.data.tags import Tag


class AnnotationTask(BaseModel):
    """Annotation task."""

    id: UUID = Field(default_factory=uuid4)
    """Unique identifier for the annotation task."""

    clip: Clip
    """The annotated clip."""

    annotations: List[Annotation] = Field(default_factory=list)
    """List of annotations in the created during the annotation task."""

    completed_by: Optional[str] = None
    """The user who completed the annotation task."""

    completed_on: Optional[datetime.datetime] = None
    """The date and time when the annotation task was completed."""

    notes: List[Note] = Field(default_factory=list)
    """Notes associated with the annotation task."""

    tags: List[Tag] = Field(default_factory=list)
    """User provided tags to the annotated clip."""

    completed: bool = False
    """Whether the annotation task has been completed."""

    def __hash__(self):
        """Compute the hash value for the annotation task."""
        return hash(self.id)
