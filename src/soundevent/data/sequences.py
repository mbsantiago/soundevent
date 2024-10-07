"""Sequences.

Animal communication is a fascinating and intricate phenomenon, often
consisting of multiple vocalizations that form a cohesive message. In the
soundevent package, we introduce the concept of a Sequence object to represent
these complex vocalization patterns. A Sequence groups together multiple sound
event objects, allowing researchers to analyze and understand the composition
and dynamics of animal communication in a structured manner.

## Flexible Modeling of Vocalization Patterns

The Sequence object is designed to provide flexibility to researchers, allowing
them to model a wide range of sequence types and behaviors. While the sound
events within a sequence should originate from the same recording, no other
restrictions are imposed, empowering researchers to tailor the structure to
their specific research needs.

## Sequence Description

Similar to individual sound events, sequences can be enriched with additional
information using tags, features, and notes. Researchers can attach categorical
tags to describe the type of sequence or the associated behavior, providing
valuable insights into the communication context. Additionally, numerical
features can capture important characteristics of the sequence, such as overall
duration, inter-pulse interval, or any other relevant acoustic properties.

## Hierarchical Structure

Furthermore, recognizing the hierarchical nature of animal communication, the
Sequence object allows the inclusion of subsequences. Researchers can specify a
parent sequence, facilitating the representation of complex hierarchical
relationships within the vocalization structure.

By incorporating sequences into the analysis workflow, researchers gain a
flexible and expressive framework to explore and study the intricacies of
animal communication. The Sequence object, along with its associated tags,
features, and hierarchical capabilities, provides a powerful tool for
understanding the rich complexity of vocalization sequences.
"""

from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.features import Feature
from soundevent.data.sound_events import SoundEvent

__all__ = ["Sequence"]


class Sequence(BaseModel):
    """Sequence Class.

    Represents a sequence of sound events in bioacoustic research. A sequence is a
    ordered collection of sound events, each characterized by its unique identifier,
    associated tags, features, and notes. Sequences can be hierarchical, allowing
    the organization of sub-sequences under parent sequences.

    Attributes
    ----------
    uuid
        A unique identifier for the sequence.
    sound_events
        A list of sound events within the sequence.
    features
        A list of features associated with the sequence, offering quantitative
        information about the sequence's acoustic characteristics.
    parent
        If the sequence is a subsequence, this attribute refers to the parent
        sequence under which the current sequence is organized.
    """

    uuid: UUID = Field(default_factory=uuid4)
    sound_events: List[SoundEvent] = Field(default_factory=list)
    features: List[Feature] = Field(default_factory=list)
    parent: Optional["Sequence"] = None
