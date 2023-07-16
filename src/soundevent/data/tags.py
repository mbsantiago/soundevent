"""Tags.

Tags are a powerful mechanism for attaching additional information and metadata
to various objects within the `soundevent` package. They offer flexibility and
enable users to add contextual details to recordings, clips, and sound events.

## Purpose and Use

Tags serve the purpose of providing special meaning and enhancing the
organization and filtering capabilities of the package. They can be applied to
different entities to provide valuable insights and facilitate efficient data
management and analysis.

## Structure

Each tag is defined as a key-value pair. The key plays a crucial role in
grouping tags into coherent categories, aiding in the organization and
filtering of tags within the application. There are no restrictions on what can
be used as a key or value, empowering users to select tags that best suit their
project requirements.

## Usage Examples

Recording Tags: Tags can be attached to recordings to provide additional
information about the recording context. For example, they can indicate the
vegetation type of the recording site, the recording device used, or the
specific recording protocol employed. These tags enable users to organize and
locate specific recordings more easily.

Clip Tags: Tags can be attached to recording clips to highlight various aspects
of the acoustic content. They can be used to list the species present within a
clip, indicate noise levels, or classify the clip's soundscape into a specific
category. Clip tags provide valuable metadata and aid in analyzing and
categorizing the audio content.

Sound Event Tags: Tags can also be attached to individual sound events within a
recording. These tags offer a detailed description of the sound event and
provide additional metadata. For instance, they can indicate the species
responsible for the sound, which is crucial for species identification and
analysis. Tags can also describe the behavior exhibited by the sound emitter,
such as mating, territorial, or alarm calls. Furthermore, tags can identify
specific syllables within a larger vocalization, facilitating granular analysis
and vocalization classification.

By utilizing tags, users can enrich their data with relevant information,
enabling advanced search, filtering, and analysis of audio recordings and
associated objects within the soundevent package.

"""

from pydantic import BaseModel

__all__ = ["Tag"]


class Tag(BaseModel):
    """Tag."""

    key: str
    """The key of the tag."""

    value: str
    """The value of the tag."""

    def __hash__(self):
        """Hash the Tag object."""
        return hash((self.key, self.value))

    def __str__(self):
        """Return the string representation of the Tag object."""
        return f"{self.key}: {self.value}"
