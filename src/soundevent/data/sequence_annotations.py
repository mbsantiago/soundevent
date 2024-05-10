"""Sequence Annotation Class."""

import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.notes import Note
from soundevent.data.sequences import Sequence
from soundevent.data.tags import Tag
from soundevent.data.users import User

__all__ = [
    "SequenceAnnotation",
]


class SequenceAnnotation(BaseModel):
    """A class representing the annotations of a sequence.

    Attributes
    ----------
    uuid
        A unique identifier for the annotation.
    sequence
        The sequence being annotated.

    Notes
    -----
        A list of notes associated with the sequence.
    tags
        The tags attached to the sequence providing semantic information.
    created_on
        The date and time the annotation was created.
    created_by
        The user who created the annotation.
    """

    uuid: UUID = Field(default_factory=uuid4, repr=False)
    sequence: Sequence
    notes: List[Note] = Field(default_factory=list, repr=False)
    tags: List[Tag] = Field(default_factory=list, repr=False)
    created_by: Optional[User] = None
    created_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        repr=False,
    )
