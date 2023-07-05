"""Notes.

Notes play a crucial role in providing additional textual context and
facilitating communication among users in the annotation process. They can be
attached to recordings, clips, or sound events, serving as a means to provide
valuable information, discuss specific aspects of the annotation, or flag
incomplete or incorrect annotations. Notes enhance collaboration and contribute
to a more comprehensive understanding of the annotated audio data.

## Contextualization and Explanation

Notes serve as a mechanism to provide contextual information or explanations
about specific annotations. They can offer insights into the environmental
conditions, recording circumstances, or any other relevant details that aid in
the interpretation of the audio data. By attaching notes to recordings, clips,
or sound events, annotators can provide valuable context to other users,
ensuring a deeper understanding of the annotated material.

## Issue Flagging and Attention

Notes can be used to flag incomplete or incorrect annotations, indicating
areas that require attention. These flagged notes serve as reminders for
further review and refinement, ensuring the accuracy and quality of the
annotations. By marking notes as issues, users can draw attention to
specific items or provide feedback that prompts further investigation or
clarification.

## Alternative Interpretations and Discussions

In cases where there may be multiple valid interpretations or alternative
explanations for a sound event, notes can be used to initiate discussions
among users. Annotators can share their perspectives, propose alternative
interpretations, or engage in dialogue to explore different viewpoints.
This collaborative approach fosters a deeper understanding of the annotated
data and encourages the exploration of diverse perspectives.

Notes provide a valuable means of communication and collaboration within the
annotation process. By attaching notes to recordings, clips, or sound events,
users can provide important contextual information, flag issues, and engage in
discussions. This enhances the quality and accuracy of the annotations and
promotes a more comprehensive understanding of the audio data among annotators
and researchers involved in the project.
"""

import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

__all__ = ["Note"]


class Note(BaseModel):
    """Schema for Note objects returned to the user."""

    uuid: UUID = Field(default_factory=uuid4)
    """The id of the note."""

    message: str
    """The message of the note."""

    created_by: Optional[str] = None
    """The id of the user who created the note."""

    is_issue: bool = False
    """Whether the note is an issue."""

    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )
    """The time at which the note was created."""

    def __hash__(self):
        """Hash the Note object."""
        return hash(self.uuid)
