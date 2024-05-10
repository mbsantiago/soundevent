"""Annotated Sound Event Class.

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
from soundevent.data.users import User

__all__ = [
    "SoundEventAnnotation",
]


class SoundEventAnnotation(BaseModel):
    """Annotation Class.

    The `Annotation` class encapsulates essential information about a specific
    annotation created within a bioacoustic research project. Annotations
    provide detailed labeling for individual sound events, enhancing the
    interpretability and utility of audio data.

    Attributes
    ----------
    uuid
        A unique identifier for the annotation, automatically generated upon creation.
        This identifier distinguishes the annotation from others and is crucial for
        referencing and management purposes.
    created_by
        The user who created the annotation, providing insights into the annotator's
        identity. This information is valuable for tracking and accountability within
        annotation projects.
    sound_event
        An instance of the `SoundEvent` class representing the specific sound event
        being annotated. Sound events define distinct audio occurrences, such as bird
        calls or animal vocalizations, and are essential for categorizing the content
        of the audio data.

    Notes
    -----
        A list of `Note` instances representing additional contextual information or
        remarks associated with the annotation. Notes can provide insights into specific
        characteristics of the sound event, aiding in the comprehensive understanding
        of the annotated data.
    tags
        A list of `Tag` instances representing user-provided tags associated with the
        annotated sound event. These tags offer additional semantic context to the
        annotation, enabling detailed classification and facilitating targeted analysis
        of the acoustic content.
    created_on
        The timestamp indicating the time at which the annotation was created. This
        information is essential for tracking the progress of an annotation task and
        understanding the chronological order of annotations within a project.
    """

    uuid: UUID = Field(default_factory=uuid4, repr=False)
    sound_event: SoundEvent
    notes: List[Note] = Field(default_factory=list, repr=False)
    tags: List[Tag] = Field(default_factory=list, repr=False)
    created_by: Optional[User] = None
    created_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        repr=False,
    )

    def __hash__(self):
        """Compute the hash of the annotation."""
        return hash(self.uuid)
