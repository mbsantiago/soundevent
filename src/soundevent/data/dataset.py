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

import os
from pathlib import Path
from typing import List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.recordings import Recording

PathLike = Union[str, os.PathLike]


class Dataset(BaseModel):
    """Dataset Class.

    The `Dataset` class represents a curated collection of audio recordings
    within the context of bioacoustic research. Datasets provide a structured
    and organized repository of audio data, enabling researchers to conduct
    experiments, develop models, and gain insights into acoustic phenomena.

    Each dataset represents a specific deployment or
    field study, ensuring the contextual integrity of the audio data. By
    associating recordings with a particular dataset, researchers maintain
    a clear understanding of the relationship between the recordings and
    their source.

    Attributes
    ----------
    id : UUID, optional
        The unique identifier of the dataset, automatically generated upon
        creation. This identifier distinguishes the dataset from others and is
        crucial for referencing and management purposes within research
        projects.
    name : str
        The name of the dataset, providing a distinctive label for the
        collection of audio recordings. The dataset name serves as a reference
        point for researchers, facilitating easy identification and
        communication about the specific dataset being utilized.
    description : str, optional
        A detailed description outlining the characteristics, objectives, and
        context of the dataset. This description offers valuable insights into
        the content of the dataset, providing researchers with context about
        the source, purpose, and potential applications of the audio
        recordings.
    recordings : List[Recording], optional
        A list of `Recording` instances representing individual audio
        recordings associated with the dataset. Recordings encapsulate audio
        data and essential metadata, providing information about the source,
        duration, and other attributes of each recording. These recordings
        serve as the primary data units within the dataset.
    """

    id: UUID = Field(default_factory=uuid4, repr=False)
    name: str
    description: Optional[str] = None
    recordings: List[Recording] = Field(default_factory=list, repr=False)

    @classmethod
    def from_directory(
        cls,
        path: PathLike,
        name: Optional[str] = None,
        description: Optional[str] = None,
        recursive: bool = True,
        compute_hash: bool = True,
    ) -> "Dataset":
        """Return a dataset from the directory.

        Reads the audio files in the directory and returns a dataset
        containing the recordings.

        Parameters
        ----------
        path : PathLike
            Path to the directory.
        recursive : bool, optional
            Whether to search the directory recursively, by default True
        compute_hash : bool, optional
            Whether to compute the hash of the audio files, by default

        Returns
        -------
        Dataset
            The dataset.

        Raises
        ------
        ValueError
            If the path is not a directory.
        """
        path = Path(path)

        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        glob_pattern = "**/*.wav" if recursive else "*.wav"

        recordings = [
            Recording.from_file(file, compute_hash=compute_hash)
            for file in path.glob(glob_pattern)
        ]

        return cls(
            name=name or path.name,
            recordings=recordings,
            description=description,
        )
