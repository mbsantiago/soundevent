"""Annotation Set.

This module defines the `AnnotationSet` class, which represents a collection of
human-provided annotations. An AnnotationSet comprises multiple annotated
clips, each corresponding to a specific audio clip with their corresponding
annotated sound events. The class provides a structured way to store and manage
human annotations related to audio clips and their sound events.
"""

import datetime
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.clip_annotations import ClipAnnotation

__all__ = [
    "AnnotationSet",
]


class AnnotationSet(BaseModel):
    """Annotation Set Class."""

    uuid: UUID = Field(default_factory=uuid4, repr=False)
    clip_annotations: List[ClipAnnotation] = Field(
        default_factory=list,
        repr=False,
    )
    created_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )
