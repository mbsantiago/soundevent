"""Recording Set."""

import datetime
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.recordings import Recording


class RecordingSet(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    recordings: List[Recording] = Field(default_factory=list, repr=False)
    created_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )
