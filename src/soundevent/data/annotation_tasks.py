import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.clips import Clip
from soundevent.data.users import User


class AnnotationState(str, Enum):
    """Annotation State Enumeration.

    Enumeration representing the different states an audio clip can be in
    during the annotation process. The `AnnotationState` enum provides clear
    insights into the progress of the annotation process, helping users
    understand the current stage of the annotation of the clip.

    Attributes
    ----------
    assigned
        The clip has been assigned to an annotator and is awaiting completion.
    completed
        The clip has been fully annotated and is awaiting review.
    verified
        The clip has been reviewed and accepted by the reviewer, indicating
        that the annotation is complete and accurate.
    rejected
        The clip annotations have been reviewed and rejected by the reviewer,
        indicating that the annotation is incomplete or inaccurate.
    """

    assigned = "assigned"
    completed = "completed"
    verified = "verified"
    rejected = "rejected"


class StatusBadge(BaseModel):
    """Annotation Status Badge Class.

    Represents an indicator of the current state of annotation for a clip.

    The StatusBadge class includes information such as the task state, the
    responsible user, and the creation timestamp, providing insights into the
    clip's annotation progress.

    Attributes
    ----------
    state
        The AnntoationState enum indicating the current state of the annotation
        of the clip.
    owner
        Optional field specifying the user responsible for this status badge.
    created_on
        The date and time when the status badge was created, providing a
        historical record of the badge's creation time.
    """

    state: AnnotationState
    owner: Optional[User] = None
    created_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )


class AnnotationTask(BaseModel):
    uuid: UUID = Field(default_factory=uuid4, repr=False)
    clip: Clip
    status_badges: List[StatusBadge] = Field(default_factory=list)
    created_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )
