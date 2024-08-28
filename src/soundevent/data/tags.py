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

import warnings
from collections.abc import Sequence
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from soundevent.data.compat import key_from_term, term_from_key
from soundevent.data.terms import Term

__all__ = ["Tag", "find_tag"]


class Tag(BaseModel):
    """Tag Class.

    Tags are essential elements in annotating and categorizing various
    components within bioacoustic research. Each tag consists of a key-value
    pair, where the key serves as a unique identifier for grouping tags into
    meaningful categories. Tags play a crucial role in organizing, filtering,
    and interpreting data within the application.

    Attributes
    ----------
    key
        The key of the tag, serving as a label or category identifier. It helps
        in organizing tags into coherent groups, enhancing the manageability of
        annotations.
    value
        The value associated with the tag, providing specific information or
        characteristics related to the key. Users have the flexibility to assign
        values based on project requirements.
    """

    model_config = ConfigDict(extra="allow")

    term: Term = Field(
        title="Term",
        description="The standardised term associated with the tag.",
        repr=False,
    )

    value: str = Field(
        title="Value",
        description="The value associated with the tag.",
        repr=True,
    )

    def __hash__(self):
        """Hash the Tag object."""
        return hash((self.term, self.value))

    @property
    def key(self) -> str:
        """Return the key of the tag."""
        warnings.warn(
            "The 'key' attribute is deprecated. Use 'term' instead.",
            DeprecationWarning,
            stacklevel=1,
        )
        return key_from_term(self.term)

    @model_validator(mode="before")
    @classmethod
    def handle_deprecated_key(cls, values):
        if "key" in values:
            warnings.warn(
                "The 'key' field is deprecated. Please use 'term' instead.",
                DeprecationWarning,
                stacklevel=1,
            )

            if "term" not in values:
                values["term"] = term_from_key(values["key"])

            del values["key"]
        return values


def find_tag(
    tags: Sequence[Tag],
    term: Optional[Term] = None,
    label: Optional[str] = None,
    default: Optional[Tag] = None,
) -> Optional[Tag]:
    """Find a tag by its key.

    This function searches for a tag with the given term or term label within
    the provided sequence of tags. If the tag is found, its corresponding Tag
    object is returned. If not found, and a default Tag object is provided, the
    default tag is returned. If neither the tag is found nor a default tag is
    provided, None is returned.

    Parameters
    ----------
    tags
        The sequence of Tag objects to search within.
    term
        The term object to search for.
    label
        The label of the term to search for.
    default
        The default Tag object to return if the tag is not found. Defaults to
        None.

    Returns
    -------
    tag
        The Tag object if found, or the default Tag object if provided. Returns
        None if the tag is not found and no default is provided.

    Notes
    -----
    If there are multiple tags with the same term or term label, the first one
    is returned.

    Raises
    ------
    ValueError
        If neither the term nor the label is provided.
    """
    if term is not None:
        return next(
            (t for t in tags if t.term == term),
            default,
        )

    if label is not None:
        return next(
            (t for t in tags if t.term.label == label),
            default,
        )

    raise ValueError("Either 'term' or 'label' must be provided.")
