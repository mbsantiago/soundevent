## Automated Analysis

### Predicted Tags

In the realm of audio analysis, machine-learning-based methods often generate
categorical descriptions of processed sound clips. These descriptions, here
defined as predicted tags, serve to capture the output of these methods.
However, in many cases, these methods operate using probabilistic models,
resulting in the assignment of **probability scores** that measure the
confidence of the [tag](#tags) assignment.

#### Probability Scores

Predicted tags not only represent categorical descriptions but also carry vital
information in the form of probability scores. These scores reflect the degree
of confidence associated with the tag assignment. Ranging from 0 to 1, a score
of 1 signifies a high level of certainty in the assigned tag. It is worth noting
that in cases where the audio analysis method does not provide a score, the
score is set to 1 as a default value.

By incorporating probability scores into predicted tags, machine learning-based
audio analysis methods provide insights into the confidence level of the
assigned [tags](#tags). Researchers can leverage this information to assess the
reliability and accuracy of the predicted tags, facilitating further analysis
and evaluation of the audio data.

### Predicted Sound Events

Predicted sound events occur frequently in the field of audio analysis, where
machine learning models and automated methods are employed to identify
[sound events](#sound_events_1) within audio [clips](#clips). These predicted
sound events represent the outputs of these methods, providing valuable insights
into the presence and characteristics of [sound events](#sound_events_1).

#### Probability Scores and Confidence

When a machine learning model or automated method identifies a sound event, it
assigns a probability **score** to indicate its confidence in the presence of
that event within the clip. This probability score reflects the degree of
certainty associated with the event's identification. Researchers can utilize
these scores to assess the reliability and accuracy of the predicted sound
events, enabling further analysis and evaluation.

#### Predicted Tags

Predicted sound events can be enriched with additional information through the
inclusion of [predicted tags](#predicted_tags). Each predicted sound event can
have multiple [predicted tags](#predicted_tags) associated with it, providing
semantic labels that offer insights into the nature and characteristics of the
event. Each [predicted tag](#predicted_tags) is assigned its own probability
score, which reflects the confidence of the model in the relevance of the tag to
the event. These scores assist researchers in understanding the significance and
reliability of the predicted tags.

#### Acoustic Features

Automated analysis methods often yield acoustic [features](#features) as a
result of their processing. These [features](#features) capture various
characteristics and properties of the predicted sound events. Researchers can
attach these automatically extracted acoustic features to the predicted sound
events, enabling a more comprehensive understanding and analysis of the events'
acoustic content.

### Processed Clips

In the field of bioacoustics, it is common to process recording [clips](#clips)
in order to extract relevant information. This processing can involve the use of
machine learning models or non-machine learning pipelines specifically designed
for tasks such as sound event detection or automated acoustic feature
extraction. The `ProcessedClip` objects encapsulate the results of these
processing steps.

#### Types of Processing Results

The `ProcessedClip` objects capture the outcomes of the processing steps applied
to the recording clips. These outcomes can take different forms:

- _Predicted Sound Events_: The processing may involve the detection or
  identification of [sound events](#sound_events_1) within the clip. The
  `ProcessedClip` object stores the
  [predicted sound events](#predicted_sound_events), providing information about
  their characteristics, such as their temporal and frequency properties.

- _Predicted Tags at Clip Level_: The processing may also generate
  [predicted tags](#predicted_tags) at the clip level, providing high-level
  semantic information about the content of the clip. These tags highlight
  specific aspects or categories of the acoustic content and can aid in the
  organization and categorization of the clips.

- _Features at Clip Level_: The processing may extract acoustic
  [features](#features) from the clip, which can capture relevant information
  about the audio content. These [features](#features) can be numerical
  representations that describe properties such as signal to noise ratio,
  spectral centroid, or other characteristics of the acoustic content of the
  clip.

#### Annotations and Additional Information

The [predicted sound events](#predicted_sound_events) within the `ProcessedClip`
object can be further enriched with [predicted tags](#predicted_tags) and/or
[features](#features) associated with each predicted sound event. These
annotations and additional information provide more detailed insights into the
predicted events and aid in subsequent analysis and interpretation.

## Model Run

In bioacoustic research, it is common to apply the same processing pipeline to a
set of audio [clips](#clips), such as all the clips in a [dataset](#datasets) or
a test set. To maintain a reference to this group of
[processed clips](#processed_clips) and the specific processing method used, the
concept of a `ModelRun` is introduced. A `ModelRun` represents a collection of
[processed clips](#processed_clips) that were generated in a single run using
the same processing method.

### Ensuring Consistency and Comparability

By organizing [processed clips](#processed_clips) into `ModelRun` objects,
researchers can ensure that all clips within a run were analyzed in the same
exact manner. This guarantees consistency and comparability when comparing
results across different runs or when evaluating against other groups of
annotations.

### Tracking Processing Method

The `ModelRun` object keeps track of the specific processing method that was
applied to generate the [processed clips](#processed_clips). This information is
crucial for reproducing and replicating the results, as well as for accurately
documenting the processing pipeline.

### Comparative Analysis and Evaluation

`ModelRun` objects facilitate comparative analysis and evaluation of different
processing methods or runs. Researchers can easily compare the results and
performance of various models, algorithms, or parameter settings by examining
the [processed clips](#processed_clips) within each `ModelRun`.
