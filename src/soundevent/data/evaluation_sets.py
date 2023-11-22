"""Evaluation Sets."""

from typing import Optional, Sequence

from pydantic import Field

from soundevent.data.annotation_sets import AnnotationSet
from soundevent.data.tags import Tag

__all__ = [
    "EvaluationSet",
]


class EvaluationSet(AnnotationSet):
    """Evaluation Set Class."""

    name: str
    description: Optional[str] = None
    evaluation_tags: Sequence[Tag] = Field(default_factory=list)
