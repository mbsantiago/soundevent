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

from soundevent.data.users import User

__all__ = ["Note"]


class Note(BaseModel):
    """Note Class.

    Notes play a pivotal role in the annotation process, providing essential
    textual context and enabling effective communication among users. Attached
    to recordings, clips, or sound events, notes serve various purposes, from
    offering contextual information and explanations to flagging issues and
    initiating discussions. This collaborative tool enhances the accuracy and
    depth of annotations while promoting a richer understanding of the audio
    data.

    Attributes
    ----------
    uuid
        A unique identifier for the note, automatically generated upon
        creation. This ID distinguishes each note, ensuring a clear reference
        for annotators and researchers.
    message
        The content of the note, which can include contextual information,
        explanations, issues, alternative interpretations, or any other
        relevant details. The message provides valuable insights and
        explanations related to the annotated material.
    created_by
        The identifier of the user who created the note. While optional,
        including this information enables users to understand the source of
        the note, fostering transparency and accountability within the
        annotation process.
    is_issue
        A flag indicating whether the note highlights an issue or concern. When
        set to True, the note signals incomplete or incorrect annotations,
        guiding annotators' attention to specific areas that require further
        review and refinement.
    created_on
        The date and time when the note was created. This timestamp provides a
        historical record of the note's origin, allowing users to track the
        timeline of annotations and discussions.
    """

    uuid: UUID = Field(default_factory=uuid4)
    message: str
    created_by: Optional[User] = None
    is_issue: bool = False
    created_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )

    def __hash__(self):
        """Hash the Note object."""
        return hash(self.uuid)
