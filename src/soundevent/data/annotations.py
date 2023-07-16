"""Annotations.

Annotations play a crucial role in the analysis and interpretation of
audio data. They are user-created sound events that are attached to
audio recordings, providing valuable information about specific sound
events or audio features within the recordings. Annotations are typically
created by annotators as part of an annotation task, where they
identify and label sound events based on their expertise and criteria.

## Tags and Features

Similar to regular sound events, annotations can be enriched with tags
and features to provide semantic meaning and additional information.
These tags and features help in identifying the characteristics of the
annotated sound event, such as the species responsible for the sound
or specific acoustic attributes. However, it is important to note that
annotations are subject to the annotator's expertise, criteria, and
biases. Therefore, the tags and features attached to annotations
should be considered as a result of the annotator's interpretation
rather than ground truth.

## User Information and Timestamps

Annotations are associated with the annotator who created them and are
timestamped to track when they were made. This user information and
timestamping serve multiple purposes. Researchers can filter and
select annotations based on the annotator or the time of annotation.
For instance, it can be used as a form of version control, allowing
researchers to retrieve annotations created before a specific date.
Additionally, researchers can attach notes to annotations to provide
contextual information or engage in discussions about the assignment
of specific tags to sound events.

## Significance in Analysis

Annotations serve as a valuable resource for audio analysis and
research. They allow researchers to capture subjective interpretations
and expert knowledge about sound events. By incorporating annotations
into the analysis pipeline, researchers can gain insights into
specific sound event characteristics, explore trends or patterns, and
compare annotations across different annotators or datasets. However,
it is crucial to differentiate annotations from ground truth sound
events, as annotations reflect individual interpretations and may
introduce subjectivity into the analysis.
"""

import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.notes import Note
from soundevent.data.sound_events import SoundEvent
from soundevent.data.tags import Tag

__all__ = [
    "Annotation",
]


class Annotation(BaseModel):
    """Annotation."""

    id: UUID = Field(default_factory=uuid4, repr=False)
    """A unique identifier for the annotation."""

    created_by: Optional[str] = None
    """The user who created the annotation."""

    sound_event: SoundEvent
    """The sound event being annotated."""

    notes: List[Note] = Field(default_factory=list, repr=False)
    """Notes associated with the annotation."""

    tags: List[Tag] = Field(default_factory=list, repr=False)
    """User provided tags to the annotated sound event."""

    created_on: Optional[datetime.datetime] = Field(
        default_factory=datetime.datetime.now, repr=False
    )
    """The time at which the annotation was created.

    Important for tracking the progress of an annotation task.
    """

    def __hash__(self):
        """Compute the hash of the annotation."""
        return hash(self.id)
