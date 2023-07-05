"""Datasets.

Datasets play a crucial role in the organization and management of
audio recordings in the field of audio analysis and research. They
serve as logical collections of audio recordings, consolidating
recordings that are associated with a specific context, such as a
deployment or field study. While datasets typically consist of
recordings captured by the same group of individuals using similar
equipment and following a predefined protocol, it is important to note
that adherence to these criteria is not mandatory.

## Naming and Description

Each dataset should be given a meaningful name and accompanied by a
descriptive summary. The name of the dataset should succinctly convey
the common theme or purpose of the recordings it contains. This
enables users to easily identify and differentiate between multiple
datasets. Additionally, the description provides valuable contextual
information about the dataset, including details about its origin,
context, and relevance, facilitating a deeper understanding of its
content.

## Advantages of Datasets

Datasets offer several advantages in the realm of audio analysis and
research:

* Organization: By systematically grouping related audio
recordings together, datasets provide an efficient approach to
organizing data. Researchers can navigate and locate specific sets
of data with ease, streamlining their workflow.

* Contextualization: Each dataset represents a specific deployment or
field study, ensuring the contextual integrity of the audio data. By
associating recordings with a particular dataset, researchers maintain
a clear understanding of the relationship between the recordings and
their source.

* Management: Datasets enable researchers to manage and manipulate
audio recordings as cohesive units. Operations such as data
preprocessing, feature extraction, and analysis can be applied to
entire datasets, simplifying the management and analysis process.

## Utilizing Datasets

By leveraging datasets, researchers can effectively structure their
audio data, ensuring ease of access, maintainability, and
reproducibility of their experiments and analyses. Datasets provide a
systematic and organized approach to managing audio recordings,
facilitating efficient research workflows and promoting robust
scientific practices.
"""

from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.recordings import Recording


class Dataset(BaseModel):
    """Datasets."""

    id: UUID = Field(default_factory=uuid4)
    """The unique identifier of the dataset."""

    name: str
    """The name of the dataset."""

    description: Optional[str] = None
    """A description of the dataset."""

    recordings: List[Recording] = Field(default_factory=list)
    """List of recordings associated with the dataset."""
