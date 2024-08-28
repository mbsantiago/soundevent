# Data Schemas

Welcome to the data schemas tour with the `soundevent` package! In this overview, we'll break down the various data schemas provided by the package into the following sections:

## Describing the Data

`soundevent` provides tools to attach essential information to various objects in bioacoustic analysis:

- [Users](descriptors.md#users): Keeping reference of everyone's contribution.
- [Terms](descriptors#terms): Standardized vocabularies ensure consistent language.
- [Tags](descriptors.md#tags): Attaching semantic context to objects.
- [Features](descriptors.md#features): Numerical descriptors capturing continuously varying attributes.
- [Notes](descriptors.md#notes): User-written free-text annotations.

## Audio Content

At the core of acoustic analysis, we have schemas for:

- [Recordings](audio_content.md#recordings): Complete audio files.
- [Dataset](audio_content.md#datasets): A collection of recordings from a common source.

## Acoustic Objects

Identifying distinctive sound elements within audio content:

- [Geometric Objects](acoustic_objects.md#geometries): Defining Regions of Interest (RoI) in the temporal-frequency plane.
- [Sound Events](acoustic_objects.md#sound_events): Individual sonic occurrences.
- [Sequences](acoustic_objects.md#sequences): Patterns of connected sound events.
- [Clips](acoustic_objects.md#clips): Fragments extracted from recordings.

## Annotation

`soundevent` places emphasis on human annotation processes, covering:

- [Sound Event Annotations](annotation.md#sound_event_annotation): Expert-created markers for relevant sound events.
- [Sequence Annotations](annotation.md#sequence_annotation): User provided annotations of sequences of sound events.
- [Clip Annotations](annotation.md#clip_annotations): Annotations and notes at the clip level.
- [Annotation Task](annotation.md#annotation_task): Descriptions of tasks and the status of annotation.
- [Annotation Project](annotation.md#annotation_project): The collective description of tasks and annotations.

## Prediction

Automated processing methods also play a role, generating:

- [Sound Event Predictions](prediction.md#sound_event_predictions): Predictions made during automated processing.
- [Sequence Predictions](prediction.md#sequence_predictions): Predictions of sequences of sound events.
- [Clip Predictions](prediction.md#clip_predictions): Collections of predictions and additional information at the clip level.
- [Model Runs](prediction.md#model_runs): Sets of clip predictions generated in a single run by a specific model.

## Evaluation

Assessing the accuracy of predictions is crucial, and `soundevent` provides schemas for:

- [Matches](evaluation.md#matches): Predicted sound events overlapping with ground truth.
- [Clip Evaluation](evaluation.md#clip_evaluation): Information about matches and performance metrics at the clip level.
- [Evaluation](evaluation.md#evaluation_1): Comprehensive details on model performance across the entire evaluation set.
- [Evaluation Set](evaluation.md#evaluation_set): Human annotations serving as ground truth.

Want to know more? Dive in for a closer look at each of these schemas.

!!! info "Unique Identifiers"

    In `soundevent`, various objects feature a field called `uuid`. This field
    stores a **Universal Unique Identifier (UUID)**, a 128-bit label generated
    automatically. When created following standard methods, UUIDs are practically
    unique. Information labeled with UUIDs by different parties can be combined
    into a unified database without fear of duplication.
