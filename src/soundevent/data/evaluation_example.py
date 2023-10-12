"""Evaluation Example module.

This module defines the `EvaluationExample` class, representing individual
examples within an evaluation set. Each `EvaluationExample` encapsulates an
audio clip, its associated annotations, and the expected outcomes for
evaluation purposes. These examples serve as the fundamental units for
evaluating machine learning models in bioacoustic analysis.
"""

from typing import Sequence
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.annotations import Annotation
from soundevent.data.clips import Clip
from soundevent.data.tags import Tag

__all__ = [
    "EvaluationExample",
]


class EvaluationExample(BaseModel):
    """Evaluation Example Class.

    Represents an individual evaluation example within an evaluation set. Each
    `EvaluationExample` encapsulates crucial information necessary for
    evaluating machine learning models in bioacoustic tasks. These examples
    consist of an audio clip, associated tags, and ground truth annotations.

    Attributes
    ----------
    uuid : UUID, optional
        A unique identifier for the evaluation example, automatically generated
        upon creation. This identifier distinguishes each example within an
        evaluation set, ensuring individuality and traceability in evaluations.
    clip : Clip
        An instance of the `Clip` class representing the audio clip associated
        with the evaluation example. The clip serves as the foundation for model
        evaluation, with its acoustic content being analyzed by the machine
        learning algorithm. Understanding the clip's characteristics is essential
        for contextualizing the model's predictions and performance.
    tags : List[Tag], optional
        A list of `Tag` instances representing categories associated with the
        audio clip. These tags provide additional context about the content of
        the clip, aiding in the evaluation process. Tags can include information
        such as species names or event types, enriching the understanding of the
        audio content and facilitating targeted analysis.
    annotations : List[Annotation], optional
        A list of `Annotation` instances representing the ground truth sound
        events within the audio clip. Annotations provide detailed information
        about sound events, including their characteristics, timing, and other
        relevant attributes. Comparing model predictions with these annotations
        enables a thorough assessment of the model's accuracy and precision.
    """

    uuid: UUID = Field(default_factory=uuid4)
    clip: Clip
    tags: Sequence[Tag] = Field(default_factory=list)
    annotations: Sequence[Annotation] = Field(default_factory=list)
