"""Annotation Projects.

The `AnnotationProject` class in the `soundevent` package
represents a collection of human-provided annotations within a
cohesive annotation project. In bioacoustic research, annotations are
typically created as part of a larger project that involves
annotating a specific underlying material, such as a set of audio
recordings. This annotation project provides instructions to
annotators, guiding them to generate annotations in a standardized
manner and with specific objectives in mind.

## Annotation Projects and Tasks

An `AnnotationProject` acts as a cohesive container, guiding annotators through
the standardized annotation process. It provides detailed instructions,
ensuring that annotations are generated consistently and with precise
objectives in mind. Within each annotation project, multiple annotation tasks
exist. Each task corresponds to a specific audio clip that necessitates full
annotation. Complete annotation implies that annotators have diligently
followed the provided instructions, resulting in comprehensive annotations for
the clip.

## Tags and Sound Event Annotations

Within each task, annotators typically add tags to provide additional semantic
information about the clip. Tags can highlight specific aspects of the acoustic
content or describe properties related to the clip. Additionally, annotators
may generate annotated sound events that represent the relevant sound events
occurring within the clip. These annotations contribute to a more detailed and
comprehensive understanding of the audio data.

The `AnnotationProject` class provides functionality to manage and
organize annotations within an annotation project. It enables
researchers to work with annotations, extract relevant information,
and perform further analysis on the annotated clips and associated
sound events. By utilizing the `AnnotationProject` class, researchers
can efficiently handle and leverage human-provided annotations in
their bioacoustic research projects.
"""

from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.annotation_tasks import AnnotationTask
from soundevent.data.tags import Tag


class AnnotationProject(BaseModel):
    """Annotation Project Class.

    Represents a comprehensive collection of human-provided annotations within
    a unified annotation project. An `AnnotationProject` comprises multiple
    annotation tasks, each corresponding to a specific audio clip, and provides
    clear instructions to annotators. It allows researchers to organize,
    manage, and analyze annotations in bioacoustic research projects.

    Attributes
    ----------
    uuid
        A unique identifier automatically generated for the annotation project.
        This identifier distinguishes the project from others, enabling
        seamless referencing and management. It is a crucial component for
        ensuring data integrity and traceability in the annotation process.
    name
        The name of the annotation project, providing a distinctive and
        informative label for the project. The project name acts as a reference
        point for researchers and annotators, facilitating easy identification
        and communication.
    description
        A detailed description outlining the objectives, scope, and specific
        characteristics of the annotation project. This description offers
        context to researchers, annotators, and other stakeholders involved in
        the project, providing a clear understanding of the project's goals and
        objectives.
    tasks
        A list of `AnnotationTask` instances representing individual annotation
        tasks within the project. Each task corresponds to a specific audio
        clip and contains detailed annotations. Annotation tasks are the
        fundamental units of annotation within the project, providing a
        structured approach to organizing annotation efforts and ensuring
        completeness in the annotation process.
    instructions
        Clear and precise instructions provided to annotators, guiding them
        through the annotation process. These instructions ensure uniformity in
        annotations and assist annotators in understanding the project's
        objectives and requirements. Well-defined instructions are essential
        for consistency and accuracy in the annotations, fostering reliable and
        high-quality annotated data.
    tags
        A list of `Tag` instances representing categories associated with
        annotations within the annotation project. These tags serve as the
        ontology of the annotation project, defining specific entities or
        events that annotators are tasked with identifying and classifying.
        Tags provide additional semantic context to annotations, enabling
        detailed classification and in-depth analysis of the acoustic content.
        The specified tags establish a standardized vocabulary used throughout
        the annotation project, ensuring consistency and precision in the
        annotation process.
    """

    uuid: UUID = Field(default_factory=uuid4, repr=False)
    name: str
    description: Optional[str] = Field(default=None, repr=False)
    tasks: List[AnnotationTask] = Field(default_factory=list, repr=False)
    instructions: Optional[str] = Field(default=None, repr=False)
    tags: List[Tag] = Field(default_factory=list)
