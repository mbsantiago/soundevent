# Annotations

## User Annotations

Annotations play a crucial role in the analysis and interpretation of audio
data. They are user-created [sound events](#sound_events_1) that are attached to
audio [recordings](#recordings), providing valuable information about specific
[sound events](#sound_events_1) or audio [features](#features) within the
recordings. Annotations are typically created by annotators as part of an
[annotation task](#tasks), where they identify and label sound events based on
their expertise and criteria.

### Tags and Features

Similar to regular [sound events](#sound_events_1), annotations can be enriched
with [tags](#tags) and [features](#features) to provide semantic meaning and
additional information. These [tags](#tags) and [features](#features) help in
identifying the characteristics of the annotated sound event, such as the
species responsible for the sound or specific acoustic attributes. However, it
is important to note that annotations are subject to the annotator's expertise,
criteria, and biases. Therefore, the [tags](#tags) and [features](#features)
attached to annotations should be considered as a result of the annotator's
interpretation rather than ground truth.

### User Information and Timestamps

Annotations are associated with the annotator who created them and are
timestamped to track when they were made. This user information and timestamping
serve multiple purposes. Researchers can filter and select annotations based on
the annotator or the time of annotation. For instance, it can be used as a form
of version control, allowing researchers to retrieve annotations created before
a specific date. Additionally, researchers can attach notes to annotations to
provide contextual information or engage in discussions about the assignment of
specific tags to sound events.

### Significance in Analysis

Annotations serve as a valuable resource for audio analysis and research. They
allow researchers to capture subjective interpretations and expert knowledge
about sound events. By incorporating annotations into the analysis pipeline,
researchers can gain insights into specific sound event characteristics, explore
trends or patterns, and compare annotations across different annotators or
datasets. However, it is crucial to differentiate annotations from ground truth
sound events, as annotations reflect individual interpretations and may
introduce subjectivity into the analysis.

## Tasks

Annotation tasks form a fundamental component of
[annotation projects](#annotation_projects) in bioacoustic research. The
`soundevent` package introduces the `AnnotationTask` object, which represents a
unit of annotation work. An annotation task corresponds to a specific
[clip](#clip) that requires thorough annotation based on provided instructions.

### Composition and Annotation Instructions

Each annotation task is composed of a distinct recording [clip](#clips) that
serves as the focus of annotation. Annotators are tasked with meticulously
annotating the [clip](#clips) according to the given annotation instructions.
These instructions serve as a guide, directing annotators to identify and
describe [sound events](#user_annotations) within the [clip](#clips), and
include any pertinent contextual [tags](#tags).

### Annotator-Provided Tags and Annotations

Annotations allow annotators to contribute their expertise and insights by
including [tags](#tags) that describe the acoustic content of the entire audio
clip. These annotator-provided [tags](#tags) offer valuable semantic
information, enhancing the overall understanding of the audio material.
Additionally, annotators identify and annotate specific
[sound events](#user_annotations) within the task clip, contributing to the
detailed analysis and characterization of the audio data.

### Notes and Completion Status

Annotations can be further enriched by including [notes](#notes), enabling
annotators to provide additional discussions, explanations, or details related
to the annotation task. Once an annotation task is completed, it should be
marked as such. In multi-annotator scenarios, registering the user who completed
the task allows for tracking and accountability.

## Annotation Projects

The `AnnotationProject` objects in the `soundevent` package represents a
collection of human-provided [annotations](#user_annotations) within a cohesive
annotation project. In bioacoustic research, [annotations](#user_annotations)
are typically created as part of a larger project that involves annotating a
specific underlying material, such as a set of audio [recordings](#recordings).
This annotation project provides instructions to annotators, guiding them to
generate annotations in a standardized manner and with specific objectives in
mind.

### Annotation Projects and Tasks

An annotation project serves as the unifying theme for grouping annotations. It
encompasses the underlying material to be annotated and provides instructions to
annotators. Within an annotation project, there are typically multiple
[annotation tasks](#tasks). Each [annotation task](#tasks) corresponds to a
single [clip](#clips) that requires full annotation. By "full annotation," we
mean that the annotators have executed the annotation instructions completely on
the given [clip](#clips).

### Tags and Sound Event Annotations

Within each task, annotators typically add [tags](#tags) to provide additional
semantic information about the [clip](#clips). [Tags](#tags) can highlight
specific aspects of the acoustic content or describe properties related to the
[clip](#clips). Additionally, annotators may generate
[annotated sound events](#user_annotations) that represent the relevant
[sound events](#sound_events_1) occurring within the clip. These annotations
contribute to a more detailed and comprehensive understanding of the audio data.

The `AnnotationProject` objects provide functionality to manage and organize
[annotations](#user_annotations) within an annotation project. It enables
researchers to work with [annotations](#user_annotations), extract relevant
information, and perform further analysis on the annotated clips and associated
sound events. By utilizing the `AnnotationProject` class, researchers can
efficiently handle and leverage human-provided annotations in their bioacoustic
research projects.
