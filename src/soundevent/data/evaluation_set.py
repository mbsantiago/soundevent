"""Evaluation Sets.

This module handles evaluation sets, which are essential for assessing the
performance of model predictions in specific bioacoustic tasks. Evaluation sets
consist of clips that have been meticulously annotated by humans. Unlike
regular annotation projects, evaluation sets are assumed to be fully and
reliably annotated.

Evaluation sets serve a distinct purpose: to evaluate the performance of a
model in a specific task, such as sound event detection. Each evaluation set is
associated with a particular task and a predefined set of classes, like bird
species.

One key feature of evaluation sets is their flexibility in assembly. They can
be created by consolidating data from multiple annotation projects. This
separation of the annotation and evaluation processes is valuable, especially
when different teams handle annotation and machine learning model development
separately.
"""

from enum import Enum
from typing import Sequence
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.evaluation_example import EvaluationExample
from soundevent.data.tags import Tag

__all__ = [
    "EvaluationSet",
    "EvaluationTask",
]


class EvaluationTask(str, Enum):
    """Enumeration of Evaluation Tasks.

    Enumeration representing different evaluation tasks for assessing
    the performance of models in bioacoustic analysis.

    Attributes
    ----------
    SOUND_EVENT_CLASSIFICATION : str
        Evaluation task focusing on assigning correct tags to individual sound
        events. The model is evaluated based on its ability to accurately
        assign a single tag to sound events (e.g., classifying a dog bark as
                                             "dog_bark").
    SOUND_EVENT_DETECTION : str
        Evaluation task assessing the model's ability to detect and classify
        sound events within a given clip. The model must identify the bounds of
        sound events and assign appropriate tags to them.
    CLIP_MULTILABEL_CLASSIFICATION : str
        Evaluation task evaluating the model's ability to assign multiple
        correct tags to a clip. For example, classifying a clip containing both
        a dog bark and a car horn as "dog_bark" and "car_horn" respectively.
    CLIP_CLASSIFICATION : str
        Evaluation task focusing on assigning a single correct tag to a clip.
        The model is evaluated on its ability to assign the correct tag to a
        clip (e.g., labeling a clip with a dog bark as "dog_bark").
    """

    SOUND_EVENT_CLASSIFICATION = "sound_event_classification"
    SOUND_EVENT_DETECTION = "sound_event_detection"
    CLIP_MULTILABEL_CLASSIFICATION = "clip_multilabel_classification"
    CLIP_CLASSIFICATION = "clip_classification"


class EvaluationSet(BaseModel):
    """Evaluation Set Class.

    The `EvaluationSet` class represents a curated set of annotated clips used
    for evaluating the performance of machine learning models in bioacoustic
    tasks. These sets are pivotal for rigorously assessing a model's ability to
    classify sound events or detect specific events within audio clips,
    providing valuable insights into the model's capabilities.

    Attributes
    ----------
    uuid : UUID, optional
        A unique identifier for the evaluation set, automatically generated
        upon creation. This identifier distinguishes each evaluation set,
        ensuring individuality and traceability in evaluations.
    name : str
        The name of the evaluation set, serving as a unique identifier for
        reference and communication. The name provides context about the
        specific collection of annotated clips being used for evaluation.
    description : str
        A detailed description of the evaluation set, outlining its purpose,
        origin, and any specific characteristics. This information helps users,
        researchers, and practitioners understand the context and objectives of
        the evaluation. Detailed descriptions are instrumental in clarifying
        the evaluation's scope and relevance.
    task : EvaluationTask
        An instance of the `EvaluationTask` enum indicating the specific
        bioacoustic task for which the evaluation set is intended. Tasks can
        include sound event classification, sound event detection, clip
        multilabel classification, or clip classification. Defining the task
        explicitly guides the evaluation process, ensuring alignment with the
        intended objectives.
    tags : List[Tag]
        A list of `Tag` instances representing the classes relevant to the
        evaluation set's task. Tags serve as the predefined categories to which
        sound events or clips are assigned during evaluation. For instance, in
        bird species classification, tags could include "sparrow," "robin," and
        "hawk." Well-defined tags establish a standardized vocabulary, ensuring
        consistency and precision in the evaluation process.
    examples : List[EvaluationExample]
        A list of `EvaluationExample` instances, each representing a clip
        within the evaluation set. These examples form the basis for evaluating
        the model's performance. Each example contains comprehensive
        information about the audio clip, its associated annotations, and the
        expected outcomes for evaluation. Properly documented examples are
        crucial for meaningful evaluation and detailed analysis of the model's
        behavior on specific instances.
    """

    uuid: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    task: EvaluationTask
    tags: Sequence[Tag] = Field(default_factory=list)
    examples: Sequence[EvaluationExample] = Field(default_factory=list)
