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
from soundevent.data.notes import Note
from soundevent.data.sound_events import SoundEvent
from soundevent.data.tags import Tag


class Sequence(BaseModel):
    """Sequences."""

    id: UUID = Field(default_factory=uuid4)
    """The unique identifier of the sequence."""

    sound_event: List[SoundEvent] = Field(default_factory=list)
    """The sound events in the sequence."""

    tags: List[Tag] = Field(default_factory=list)
    """The tags describing the sequence."""

    features: List[Feature] = Field(default_factory=list)
    """Features associated with the sequence."""

    notes: List[Note] = Field(default_factory=list)
    """Notes about the sequence."""

    parent: Optional["Sequence"] = None
    """If the sequence is a subsequence, this is the parent sequence."""
