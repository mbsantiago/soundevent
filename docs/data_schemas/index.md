# Data Schemas

Welcome to the data schemas tour with the `soundevent` package! In this
overview, we'll break down the various data schemas provided by the package into
the following sections:

## Describing the Data

`soundevent` equips you with tools to attach crucial information to diverse
objects encountered in bioacoustic analysis. These include:

- [Users](descriptors/#users): Keeping reference of everyone's contribution.
- [Tags](descriptors/#tags): Attaching semantic context to objects.
- [Features](descriptors/#features): Numerical descriptors capturing
  continuously varying attributes.
- [Notes](descriptors/#notes): User-written free-text annotations.

## Audio Content

Delving into the core of acoustic analysis, we have schemas for:

- [Recordings](audio_content/#recordins): Complete audio files.
- [Dataset](audio_content/#datasets): A collection of recordings from a common
  source.

## Acoustic Objects

Identifying distinctive sound elements within audio content, we have:

- [Geometric Objects](acoustic_objects/#geometries): Defining Regions of
  Interest (RoI) in the temporal-frequency plane.
- [Sound Events](acoustic_objects/#sound_events): Individual sonic occurrences.
- [Sequences](acoustic_objects/#sequences): Patterns of connected sound events.
- [Clips](acoustic_objects/#clips): Fragments extracted from recordings.

## Annotation

`soundevent` places emphasis on human annotation processes, covering:

- [Sound Event Annotations](annotation/#sound_event_annotation): Expert-created
  markers for relevant sound events.
- [Sequence Annotations](annotation/#sequence_annotation): User provided
  annotations of sequences of sound events.
- [Clip Annotations](annotation/#clip_annotations): Annotations and notes at the
  clip level.
- [Annotation Task](annotation/#annotation_task): Descriptions of tasks and the
  status of annotation.
- [Annotation Project](annotation/#annotation_project): The collective
  description of tasks and annotations.

## Prediction

Automated processing methods also play a role, generating:

- [Sound Event Predictions](prediction/#sound_event_predictions): Predictions
  made during automated processing.
- [Sequence Predictions](prediction/#sequence_predictions): Predictions of
  sequences of sound events.
- [Clip Predictions](prediction/#clip_predictions): Collections of predictions
  and additional information at the clip level.
- [Model Runs](prediction/#model_runs): Sets of clip predictions generated in a
  single run by a specific model.

## Evaluation

Assessing the accuracy of predictions is crucial, and `soundevent` provides
schemas for:

- [Matches](evaluation/#matches): Predicted sound events overlapping with ground
  truth.
- [Clip Evaluation](evaluation/#clip_evaluation): Information about matches and
  performance metrics at the clip level.
- [Evaluation](evaluation/#evaluation_1): Comprehensive details on model
  performance across the entire evaluation set.
- [Evaluation Set](evaluation/#evaluation_set): Human annotations serving as
  ground truth.

Want to know more? Dive in for a closer look at each of these schemas.

!!! info "Unique Identifiers"

    In `soundevent`, various objects feature a field called `uuid`. This field
    stores a **Universal Unique Identifier (UUID)**, a 128-bit label generated
    automatically. When created following standard methods, UUIDs are practically
    unique. Information labeled with UUIDs by different parties can be combined
    into a unified database without fear of duplication.
