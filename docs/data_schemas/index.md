# Data Schemas

Welcome to the data schemas tour with the `soundevent` package! In this
overview, we'll break down the various data schemas provided by the package into
the following sections:

## Describing the Data

`soundevent` equips you with tools to attach crucial information to diverse
objects encountered in bioacoustic analysis. These include:

- Tags: Attaching semantic context to objects.
- Features: Numerical descriptors capturing continuously varying attributes.
- Notes: User-written free-text annotations.

## Audio Content

Delving into the core of acoustic analysis, we have schemas for:

- Recordings: Complete audio files.
- Clips: Fragments extracted from recordings.
- Dataset: A collection of recordings from a common source.

## Acoustic Objects

Identifying distinctive sound elements within audio content, we have:

- Geometric Objects: Defining Regions of Interest (RoI) in the
  temporal-frequency plane.
- Sound Events: Individual sonic occurrences.
- Sequences: Patterns of connected sound events.

## Annotation

`soundevent` places emphasis on human annotation processes, covering:

- Sound Event Annotations: Expert-created markers for relevant sound events.
- Clip Annotations: Annotations and notes at the clip level.
- Annotation Task: Descriptions of tasks and the status of annotation.
- Annotation Project: The collective description of tasks and annotations.

## Prediction

Automated processing methods also play a role, generating:

- Sound Event Predictions: Predictions made during automated processing.
- Clip Predictions: Collections of predictions and additional information at the
  clip level.
- Model Run: Sets of clip predictions generated in a single run by a specific
  model.

## Evaluation

Assessing the accuracy of predictions is crucial, and soundevent provides
schemas for:

- Evaluation Set: Human annotations serving as ground truth.
- Matches: Predicted sound events overlapping with ground truth.
- Clip Evaluation: Information about matches and performance metrics at the clip
  level.
- Evaluation: Comprehensive details on model performance across the entire
  evaluation set.

Want to know more? Dive in for a closer look at each of these schemas.
