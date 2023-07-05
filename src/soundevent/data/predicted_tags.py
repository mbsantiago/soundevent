"""Predicted tags.

In the realm of audio analysis, machine-learning-based methods often
generate categorical descriptions of processed sound clips. These
descriptions, here defined as predicted tags, serve to capture the
output of these methods. However, in many cases, these methods
operate using probabilistic models, resulting in the assignment of
probability scores that measure the confidence of the tag assignment.

## Probability Scores

Predicted tags not only represent categorical descriptions but also
carry vital information in the form of probability scores. These
scores reflect the degree of confidence associated with the tag
assignment. Ranging from 0 to 1, a score of 1 signifies a high level
of certainty in the assigned tag. It is worth noting that in cases
where the audio analysis method does not provide a score, the score
is set to 1 as a default value.

By incorporating probability scores into predicted tags, machine
learning-based audio analysis methods provide insights into the
confidence level of the assigned tags. Researchers can leverage this
information to assess the reliability and accuracy of the predicted
tags, facilitating further analysis and evaluation of the audio data.
"""
from pydantic import BaseModel, Field

from soundevent.data.tags import Tag

__all__ = [
    "PredictedTag",
]


class PredictedTag(BaseModel):
    """Predicted tag."""

    tag: Tag
    """Predicted tag."""

    score: float = Field(default=1, ge=0, le=1)
    """The probability score of the predicted tag."""
