"""Annotation Sets.

This module defines the `AnnotationSet` class, which is used to group
human-provided annotations made on a collection of audio clips. In bioacoustic
analysis or speech processing, researchers and annotators often create labels or
descriptions (annotations) for specific sound events within audio recordings. An
`AnnotationSet` serves as a container to organize these related annotations.

Organizing annotations into sets allows for easier management, review, and use
in training machine learning models or evaluating system performance. For
instance, an `AnnotationSet` might represent all annotations created by a
specific annotator for a particular dataset, or a consensus annotation set
agreed upon by multiple annotators.
"""

import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.clip_annotations import ClipAnnotation

__all__ = [
    "AnnotationSet",
]


class AnnotationSet(BaseModel):
    """A collection of annotations for multiple audio clips.

    The `AnnotationSet` class groups together `ClipAnnotation` objects,
    representing human-provided annotations related to a set of audio clips.

    Attributes
    ----------
    uuid
        A unique identifier for the annotation set, automatically generated.
    clip_annotations
        A list of `ClipAnnotation` objects, where each object contains the
        annotations associated with a specific audio clip within this set.
    created_on
        The date and time when the `AnnotationSet` object was created.
    name
        An optional name for the annotation set
        (e.g., "Expert Annotator Set 1").
    description
        An optional detailed description of the annotation set, providing
        context about its origin, purpose, or the annotation guidelines used.
    """

    uuid: UUID = Field(default_factory=uuid4, repr=False)
    clip_annotations: List[ClipAnnotation] = Field(
        default_factory=list,
        repr=False,
    )
    created_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )
    name: Optional[str] = None
    description: Optional[str] = None
