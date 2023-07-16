"""Annotation Projects.

The `AnnotationProject` class in the `soundevent` package
represents a collection of human-provided annotations within a
cohesive annotation project. In bioacoustic research, annotations are
typically created as part of a larger project that involves
annotating a specific underlying material, such as a set of audio
recordings. This annotation project provides instructions to
annotators, guiding them to generate annotations in a standardized
manner and with specific objectives in mind.

## Annotation Projects and Tasks

An annotation project serves as the unifying theme for grouping
annotations. It encompasses the underlying material to be annotated
and provides instructions to annotators. Within an annotation
project, there are typically multiple annotation tasks. Each
annotation task corresponds to a single clip that requires full
annotation. By "full annotation," we mean that the annotators have
executed the annotation instructions completely on the given clip.

## Tags and Sound Event Annotations

Within each task, annotators typically add tags to provide additional semantic
information about the clip. Tags can highlight specific aspects of the acoustic
content or describe properties related to the clip. Additionally, annotators
may generate annotated sound events that represent the relevant sound events
occurring within the clip. These annotations contribute to a more detailed and
comprehensive understanding of the audio data.

The `AnnotationProject` class provides functionality to manage and
organize annotations within an annotation project. It enables
researchers to work with annotations, extract relevant information,
and perform further analysis on the annotated clips and associated
sound events. By utilizing the `AnnotationProject` class, researchers
can efficiently handle and leverage human-provided annotations in
their bioacoustic research projects.
"""

from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.annotation_tasks import AnnotationTask


class AnnotationProject(BaseModel):
    """Annotation collection."""

    id: UUID = Field(default_factory=uuid4, repr=False)
    """Unique identifier for the annotation collection."""

    name: str
    """Name of the annotation project."""

    description: Optional[str] = Field(default=None, repr=False)
    """Description of the annotation collection."""

    tasks: List[AnnotationTask] = Field(default_factory=list, repr=False)
    """List of annotation tasks in the project."""

    instructions: Optional[str] = Field(default=None, repr=False)
    """Instructions for annotators."""
