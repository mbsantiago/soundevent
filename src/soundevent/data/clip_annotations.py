"""Module for managing annotations related to audio clips.

This module defines the `ClipAnnotations` class, representing a collection of
annotations associated with a specific audio clip. It includes details about
the clip, associated tags, annotations, status badges indicating the state of
the annotation process, and any additional notes related to the annotations.
"""
import datetime
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.clips import Clip
from soundevent.data.notes import Note
from soundevent.data.sound_event_annotations import SoundEventAnnotation
from soundevent.data.tags import Tag

__all__ = [
    "ClipAnnotations",
]


class ClipAnnotations(BaseModel):
    """Clip Annotations Class.

    Represents annotations associated with a specific audio clip.

    ClipAnnotations encapsulates details about the audio clip, associated tags,
    annotations of sound events, status badges indicating the state of the
    annotation process, and any additional notes related to the annotations.

    Attributes
    ----------
    uuid
        A unique identifier automatically generated for the clip annotations.
    clip
        The Clip instance representing the audio clip associated with these annotations.
    tags
        A list of Tag instances defining the set of tags associated with the clip.
    annotations
        A list of Annotation instances representing detailed annotations of
        sound events in the clip.
    notes
        A list of Note instances representing additional contextual
        information or remarks associated with the clip.
    """

    uuid: UUID = Field(default_factory=uuid4)
    clip: Clip
    tags: List[Tag] = Field(default_factory=list)
    annotations: List[SoundEventAnnotation] = Field(default_factory=list)
    notes: List[Note] = Field(default_factory=list)
    created_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )
