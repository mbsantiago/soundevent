# Introduction

The `soundevent` package introduces a set of data classes that play a central
role in conceptualizing and standardizing recurrent objects in computational
bioacoustic analysis. These data classes establish clear relationships between
different concepts and define the attributes that each object possesses. With
their flexibility, they cater to a wide range of use cases within bioacoustic
analysis.

This page provides a comprehensive overview of the data objects defined within
the `soundevent` package, specifically designed for bioacoustic analysis. It
covers the following key topics:

- [Tags, Features, and Notes](#data-description): These data objects allow for
  the attachment of meaningful semantic information to enhance the description
  of bioacoustic data.

  - Tags
  - Features
  - Notes

- [Recordings and Clips](#recordings-and-clips): Descriptions of audio files and
  fragments of recordings, which serve as the source material for bioacoustic
  analysis.

  - Recording
  - Clip

- [Sound Event](#sound_events): Clear definition and methods of locating sound
  events within a recording, including different geometries.

  - GeometryType
  - Geometry
  - SoundEvent

- [Annotation](#annotations): Objects related to the process of audio
  annotation, including human-labeled sound events (annotations) and clip
  annotations.

  - Annotation
  - ClipAnnotations
  - Sequence

- [Automated Analysis](#automated_analysis): Objects that emerge from
  computational methods applied to audio, such as predicted tags, predicted
  sound events, and clip predictions.

  - PredictedTag
  - PredictedSoundEvent
  - ClipPredictions

- [Collections](#collections): Abstractions for handling collections of audio
  recordings, annotations, and predictions.

  - Dataset
  - AnnotationSet
  - PredictionSet

- Collections with Purpose:

  - Dataset
  - EvaluationSet
  - AnnotationProjects:
    - AnnotationProject
    - AnnotationState
    - StatusBadge
  - ModelRuns:
    - ModelInfo

- [Evaluation](#evaluation): Objects related to the evaluation process, such as
  the Matching between sound events, used in assessing the performance of
  analysis pipelines.

  - Match
  - ClipEvaluation
  - Evaluation

By understanding and utilizing these data objects, researchers can effectively
analyze and interpret bioacoustic data, enabling meaningful insights and
advancements in the field of bioacoustic research.

## Data Description

Discover how [tags](#tags), [features](#features), and [notes](#notes) enhance
data descriptions in bioacoustic research. Categorical tags, numerical features,
and freeform notes enrich the understanding and analysis of research objects,
facilitating comprehensive and structured information.

### Tags

Tags are a powerful mechanism for attaching additional categorical information
and metadata to various objects within the `soundevent` package. They offer
flexibility and enable researchers to add contextual details to
[recordings](#recordings), [clips](#clips), and [sound events](#sound_events_1).

#### Purpose and Use

Tags serve the purpose of providing special meaning and enhancing the
organization and filtering capabilities of the package. They can be applied to
different entities to provide valuable insights and facilitate efficient data
management and analysis.

#### Structure

Each tag is defined as a **key**-**value** pair of text. The key plays a crucial
role in grouping tags into coherent categories, aiding in the organization and
filtering of tags within the application. There are no restrictions on what can
be used as a key or value, empowering researchers to select tags that best suit
their project requirements.

#### Usage Examples

- _Recording Tags_: Tags can be attached to [recordings](#recordings) to provide
  additional information about the recording context. For example, they can
  indicate the vegetation type of the recording site, the recording device used,
  or the specific recording protocol employed. These tags enable researchers to
  organize and locate specific recordings more easily.

- _Clip Tags_: Tags can be attached to recording [clips](#clips) to highlight
  various aspects of the acoustic content. They can be used to list the species
  present within a clip, indicate noise levels, or classify the clip's
  soundscape into a specific category. Clip tags provide valuable metadata and
  aid in analyzing and categorizing the audio content.

- _Sound Event Tags_: Tags can also be attached to individual
  [sound events](#sound_events_1) within a recording. These tags offer a
  detailed description of the sound event and provide additional metadata. For
  instance, they can indicate the species responsible for the sound, which is
  crucial for species identification and analysis. Tags can also describe the
  behavior exhibited by the sound emitter, such as mating, territorial, or alarm
  calls. Furthermore, tags can identify specific syllables within a larger
  vocalization, facilitating granular analysis and vocalization classification.

By utilizing tags, researchers can enrich their data with relevant information,
enabling advanced search, filtering, and analysis of audio recordings and
associated objects within the `soundevent` package.

### Features

Features are numerical values that can be associated with
[sound events](#sound_events_1), [clips](#clips), and [recordings](#recordings).
They provide additional information and metadata, enriching the objects they are
attached to. Features play a crucial role in searching, organizing, and
analyzing bioacoustic data. Each feature consists of a **name** that describes
the characteristic it represents, and a corresponding numeric **value** that
quantifies the feature.

#### Usage Examples

- _Sound Event Features_: Features attached to [sound events](#sound_events_1)
  offer various types of information. They can provide basic characteristics,
  such as duration or bandwidth, which give a general description of the sound
  event. Additionally, features can capture more intricate details that are
  extracted using deep learning models. These details might include specific
  temporal or spectral properties of the sound event, aiding in fine-grained
  analysis and classification.

- _Clip Features_: Features associated with [clips](#clips) describe the
  acoustic content of the entire soundscape within the clip. They offer insights
  into the overall characteristics of the audio, beyond individual sound events.
  Examples of clip-level features include signal-to-noise ratio, acoustic
  indices, or other statistical measures that summarize the properties of the
  sound within the clip.

- _Recording Features_: Features can also be attached to
  [recordings](#recordings), providing contextual information of a numeric
  nature. These features offer additional metadata about the recording session,
  such as the temperature, wind speed, or other environmental conditions at the
  time of recording. They can also include characteristics of the recording
  device, such as the height of the recorder or other relevant parameters.

#### Exploring and Analyzing Annotations

By having multiple features attached to [sound events](#sound_events_1),
[clips](#clips), and [recordings](#recordings), researchers gain the ability to
explore and analyze their data more comprehensively. Features allow for the
identification of outliers, understanding the distribution of specific
characteristics across a collection of sound events, and conducting statistical
analyses.

### Notes

Notes play a crucial role in providing additional textual context and
facilitating communication among researchers. They can be attached to
[recordings](#recordings), [clips](#clips), or [sound events](#sound_events_1),
serving as a means to provide valuable information, discuss specific aspects of
the annotation, or flag incomplete or incorrect annotations. Notes enhance
collaboration and contribute to a more comprehensive understanding of the
annotated audio data.

#### Contextualization and Explanation

Notes serve as a mechanism to provide contextual information or explanations
about specific annotations. They can offer insights into the environmental
conditions, recording circumstances, or any other relevant details that aid in
the interpretation of the audio data. By attaching notes to recordings, clips,
or sound events, annotators can provide valuable context to other researchers,
ensuring a deeper understanding of the material.

#### Issue Flagging and Attention

Notes can be used to flag incomplete or incorrect annotations, indicating areas
that require attention. These flagged notes serve as reminders for further
review and refinement, ensuring the accuracy and quality of the annotations. By
marking notes as issues, researchers can draw attention to specific items or
provide feedback that prompts further investigation or clarification.

#### Alternative Interpretations and Discussions

In cases where there may be multiple valid interpretations or alternative
explanations for a sound event, notes can be used to initiate discussions among
researchers. Annotators can share their perspectives, propose alternative
interpretations, or engage in dialogue to explore different viewpoints. This
collaborative approach fosters a deeper understanding of the annotated data and
encourages the exploration of diverse perspectives.

## Recordings and Clips

### Recordings

A recording represents a single audio file, typically an unmodified file
capturing the original audio as recorded by an audio recorder. Each recording is
uniquely identified by a **hash** or other unique identifier and is associated
with a file **path** pointing to the audio file itself. In addition to the audio
data, recordings often include relevant metadata that provides essential
information about the recording.

#### Metadata

Recordings can be accompanied by metadata that offers valuable contextual
information. This metadata typically includes the **duration** of the recording,
**sample rate**, and the **number of audio channels**. These details help in
understanding the technical characteristics of the audio data and ensure
accurate processing and analysis.

#### Date, Time, and Location Information

To provide temporal and spatial context, recordings can include **date** and
**time** information indicating when they were recorded. This allows for
organizing and comparing recordings based on the time of capture. **Latitude**
and **longitude** coordinates can also be associated with a recording,
indicating the geographical location where it was recorded. This information is
particularly useful in bioacoustic research and conservation efforts for
understanding species distributions and habitat characteristics.

#### Extending Metadata

Metadata about a recording can be further enriched by attaching additional
[tags](#tags) or [features](#features). [Tags](#tags) provide categorical
information, such as the recording site, habitat type, or equipment used.
[Features](#features), on the other hand, offer numeric values that quantify
specific characteristics of the recording, such as temperature, wind speed, or
the height of the recording device.

#### Textual Notes

Recordings can also have textual [notes](#notes) attached to them, allowing
users to add descriptive information, comments, or discussion points. These
[notes](#notes) provide additional context, insights, or relevant details that
contribute to a deeper understanding of the recording.

The combination of metadata, [tags](#tags), [features](#features), and textual
[notes](#notes) associated with recordings facilitates effective organization,
searchability, and analysis of audio data in bioacoustic research and related
fields.

### Clips

A clip represents a contiguous fragment of a [recording](#recording), defined by
its **start** and **end** times. While [recordings](#recordings) serve as the
base source of information, clips are the fundamental unit of work in many
[analysis](#automated_analysis) and [annotation tasks](#annotations). When
annotating audio or running machine learning models, the focus is often on
working with clips rather than the entire recording.

#### Benefits of Using Clips

There are several reasons for using clips in audio analysis and annotation
tasks. Firstly, working with very long audio files can be computationally
prohibitive for tasks such as visualization and annotation. Breaking the
[recording](#recordings) into smaller clips improves efficiency and enables
focused analysis on specific segments of interest. Secondly, standardizing the
duration of clips allows for consistent and comparable annotations across
different [recordings](#recordings). It provides a consistent unit of analysis,
making it easier to interpret and compare results across various audio data.
Lastly, many machine learning models process audio files in clips, generating
predictions or insights per clip, which further justifies the adoption of the
clip structure.

#### Tags and Features

In acoustic analysis, understanding the content and characteristics of a clip is
a key focus. Once this information is obtained, it becomes crucial to
effectively attach and represent this knowledge. One way to achieve this is
through the use of [tags](#tags), which can include the identification of
species present in the clip, descriptions of the acoustic scene, or other
relevant categorical information. Additionally, numerical attributes of the
acoustic content, such as spectral features or temporal properties, can be
represented as [features](#features) attached to the clip. It is important to
emphasize that these attached [tags](#tags) and [features](#features) represent
the "true" or "ground-truth" attributes of the sound in the clip and its
associated sound events.

By utilizing clips as the unit of analysis and annotation, researchers and
practitioners can effectively manage and analyze audio data, enabling consistent
and granular examination of specific segments within a recording.

## Sound Events

### Sound Events

The `soundevent` package is designed to focus on the analysis of sound events,
which play a crucial role in bioacoustic research. Sound events refer to
distinct and discernible sounds within a [recording](#recordings) that are of
particular interest for analysis. A recording can contain multiple sound events
or none at all, depending on the audio content.

#### Identification and Localization

Sound events typically occur within a specific time range and occupy a limited
frequency space within a [recording](#recordings). There are various methods to
specify the location of these events, such as indicating the onset timestamp,
start and end times, or providing detailed information about the associated time
and frequency regions. These approaches enable precise localization and
description of sound events within the [recording](#recordings).

#### Tags and Semantic Information

To provide meaningful context, sound events can be enriched with [tags](#tags),
which are labels attached to the events. These tags offer semantic information
about the sound events, including the species responsible for the sound, the
behavior exhibited by the sound emitter, or even the specific syllable within a
vocalization. Tags aid in organizing and categorizing sound events, enabling
more efficient analysis and interpretation.

#### Features and Numerical Descriptors

In addition to [tags](#tags), sound events can be characterized by
[features](#features), which are numerical descriptors attached to the events.
These features provide quantitative information about the sound events, such as
duration, bandwidth, peak frequency, and other detailed measurements that can be
extracted using advanced techniques like deep learning models.
[Features](#features) offer valuable insights into the acoustic properties of
the sound events.

### Geometries

[Sound event](#sound_events_1) **geometry** plays a crucial role in locating and
describing sound events within a recording. Different geometry types offer
flexibility in representing the location of sound events, allowing for varying
levels of detail and precision. The `soundevent` package follows the
[GeoJSON](https://geojson.org/) specification for **geometry types** and
provides support for a range of geometry types.

#### Units and Time Reference

All geometries in the `soundevent` package utilize **seconds** as the unit for
time and **hertz** as the unit for frequency. It is important to note that time
values are always **relative to the start of the recording**. By consistently
using these units, it becomes easier to develop functions and interact with
geometry objects based on convenient assumptions.

#### Supported Geometry Types

The `soundevent` package supports the following geometry types, each serving a
specific purpose in describing the location of sound events:

- _Onset_: Represents a single point in time.

- _Interval_: Describes a time interval, indicating a range of time within which
  the sound event occurs.

- _Point_: Represents a specific point in time and frequency, pinpointing the
  exact location of the sound event.

- _Line_: Represents a sequence of points in time and frequency, allowing for
  the description of continuous sound events.

- _Polygon_: Defines a closed shape in time and frequency, enabling the
  representation of complex sound event regions.

- _Box_: Represents a rectangle in time and frequency, useful for specifying
  rectangular sound event areas.

- _Multi-Point_: Describes a collection of points, allowing for the
  representation of multiple sound events occurring at different locations.

- _Multi-Line_ String: Represents a collection of line strings, useful for
  capturing multiple continuous sound events.

- _Multi-Polygon_: Defines a collection of polygons, accommodating complex and
  overlapping sound event regions.

By offering these geometry types, the `soundevent` package provides a
comprehensive framework for accurately and flexibly describing the location and
extent of [sound events](#sound_events_1) within a [recording](#recordings).

### Sequences

Animal communication is a fascinating and intricate phenomenon, often consisting
of multiple vocalizations that form a cohesive message. In the `soundevent`
package, we introduce the concept of a `Sequence` object to represent these
complex vocalization patterns. A `Sequence` groups together multiple
[sound event](#sound-events) objects, allowing researchers to analyze and
understand the composition and dynamics of animal communication in a structured
manner.

#### Flexible Modeling of Vocalization Patterns

The `Sequence` object is designed to provide flexibility to researchers,
allowing them to model a wide range of sequence types and behaviors. While the
[sound events](#sound_events_1) within a sequence should originate from the same
recording, no other restrictions are imposed, empowering researchers to tailor
the structure to their specific research needs.

#### Sequence Description

Similar to individual [sound events](#sound_events_1), sequences can be enriched
with additional information using [tags](#tags), [features](#features), and
[notes](#notes). Researchers can attach categorical [tags](#tags) to describe
the type of sequence or the associated behavior, providing valuable insights
into the communication context. Additionally, numerical [features](#features)
can capture important characteristics of the sequence, such as overall duration,
inter-pulse interval, or any other relevant acoustic properties.

#### Hierarchical Structure

Furthermore, recognizing the hierarchical nature of animal communication, the
`Sequence` object allows the inclusion of subsequences. Researchers can specify
a parent sequence, facilitating the representation of complex hierarchical
relationships within the vocalization structure.

By incorporating sequences into the analysis workflow, researchers gain a
flexible and expressive framework to explore and study the intricacies of animal
communication. The `Sequence` object, along with its associated tags, features,
and hierarchical capabilities, provides a powerful tool for understanding the
rich complexity of vocalization sequences.

## Annotations

### User Annotations

Annotations play a crucial role in the analysis and interpretation of audio
data. They are user-created [sound events](#sound_events_1) that are attached to
audio [recordings](#recordings), providing valuable information about specific
[sound events](#sound_events_1) or audio [features](#features) within the
recordings. Annotations are typically created by annotators as part of an
[annotation task](#tasks), where they identify and label sound events based on
their expertise and criteria.

#### Tags and Features

Similar to regular [sound events](#sound_events_1), annotations can be enriched
with [tags](#tags) and [features](#features) to provide semantic meaning and
additional information. These [tags](#tags) and [features](#features) help in
identifying the characteristics of the annotated sound event, such as the
species responsible for the sound or specific acoustic attributes. However, it
is important to note that annotations are subject to the annotator's expertise,
criteria, and biases. Therefore, the [tags](#tags) and [features](#features)
attached to annotations should be considered as a result of the annotator's
interpretation rather than ground truth.

#### User Information and Timestamps

Annotations are associated with the annotator who created them and are
timestamped to track when they were made. This user information and timestamping
serve multiple purposes. Researchers can filter and select annotations based on
the annotator or the time of annotation. For instance, it can be used as a form
of version control, allowing researchers to retrieve annotations created before
a specific date. Additionally, researchers can attach notes to annotations to
provide contextual information or engage in discussions about the assignment of
specific tags to sound events.

#### Significance in Analysis

Annotations serve as a valuable resource for audio analysis and research. They
allow researchers to capture subjective interpretations and expert knowledge
about sound events. By incorporating annotations into the analysis pipeline,
researchers can gain insights into specific sound event characteristics, explore
trends or patterns, and compare annotations across different annotators or
datasets. However, it is crucial to differentiate annotations from ground truth
sound events, as annotations reflect individual interpretations and may
introduce subjectivity into the analysis.

### Tasks

Annotation tasks form a fundamental component of
[annotation projects](#annotation_projects) in bioacoustic research. The
`soundevent` package introduces the `AnnotationTask` object, which represents a
unit of annotation work. An annotation task corresponds to a specific
[clip](#clip) that requires thorough annotation based on provided instructions.

#### Composition and Annotation Instructions

Each annotation task is composed of a distinct recording [clip](#clips) that
serves as the focus of annotation. Annotators are tasked with meticulously
annotating the [clip](#clips) according to the given annotation instructions.
These instructions serve as a guide, directing annotators to identify and
describe [sound events](#user_annotations) within the [clip](#clips), and
include any pertinent contextual [tags](#tags).

#### Annotator-Provided Tags and Annotations

Annotations allow annotators to contribute their expertise and insights by
including [tags](#tags) that describe the acoustic content of the entire audio
clip. These annotator-provided [tags](#tags) offer valuable semantic
information, enhancing the overall understanding of the audio material.
Additionally, annotators identify and annotate specific
[sound events](#user_annotations) within the task clip, contributing to the
detailed analysis and characterization of the audio data.

#### Notes and Completion Status

Annotations can be further enriched by including [notes](#notes), enabling
annotators to provide additional discussions, explanations, or details related
to the annotation task. Once an annotation task is completed, it should be
marked as such. In multi-annotator scenarios, registering the user who completed
the task allows for tracking and accountability.

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

## Collections

### Datasets

Datasets play a important role in the organization and management of audio
[recordings](#recordings) in the field of audio analysis and research. They
serve as logical collections of audio [recordings](#recordings), consolidating
recordings that are associated with a specific context, such as a deployment or
field study. While datasets typically consist of recordings captured by the same
group of individuals using similar equipment and following a predefined
protocol, it is important to note that adherence to these criteria is not
mandatory.

#### Naming and Description

Each dataset should be given a meaningful **name** and accompanied by a
**descriptive summary**. The name of the dataset should succinctly convey the
common theme or purpose of the recordings it contains. This enables users to
easily identify and differentiate between multiple datasets. Additionally, the
description provides valuable contextual information about the dataset,
including details about its origin, context, and relevance, facilitating a
deeper understanding of its content.

#### Advantages of Datasets

Datasets offer several advantages in the realm of audio analysis and research:

- _Organization_: By systematically grouping related audio
  [recordings](#recordings) together, datasets provide an efficient approach to
  organizing data. Researchers can navigate and locate specific sets of data
  with ease, streamlining their workflow.

- _Contextualization_: Each dataset represents a specific deployment or field
  study, ensuring the contextual integrity of the audio data. By associating
  [recordings](#recordings) with a particular dataset, researchers maintain a
  clear understanding of the relationship between the recordings and their
  source.

- _Management_: Datasets enable researchers to manage and manipulate audio
  [recordings](#recordings) as cohesive units. Operations such as data
  preprocessing, feature extraction, and analysis can be applied to entire
  datasets, simplifying the management and analysis process.

#### Utilizing Datasets

By leveraging datasets, researchers can effectively structure their audio data,
ensuring ease of access, maintainability, and reproducibility of their
experiments and analyses. Datasets provide a systematic and organized approach
to managing audio [recordings](#recordings), facilitating efficient research
workflows and promoting robust scientific practices.

### Annotation Projects

The `AnnotationProject` objects in the `soundevent` package represents a
collection of human-provided [annotations](#user_annotations) within a cohesive
annotation project. In bioacoustic research, [annotations](#user_annotations)
are typically created as part of a larger project that involves annotating a
specific underlying material, such as a set of audio [recordings](#recordings).
This annotation project provides instructions to annotators, guiding them to
generate annotations in a standardized manner and with specific objectives in
mind.

#### Annotation Projects and Tasks

An annotation project serves as the unifying theme for grouping annotations. It
encompasses the underlying material to be annotated and provides instructions to
annotators. Within an annotation project, there are typically multiple
[annotation tasks](#tasks). Each [annotation task](#tasks) corresponds to a
single [clip](#clips) that requires full annotation. By "full annotation," we
mean that the annotators have executed the annotation instructions completely on
the given [clip](#clips).

#### Tags and Sound Event Annotations

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

### Model Run

In bioacoustic research, it is common to apply the same processing pipeline to a
set of audio [clips](#clips), such as all the clips in a [dataset](#datasets) or
a test set. To maintain a reference to this group of
[processed clips](#processed_clips) and the specific processing method used, the
concept of a `ModelRun` is introduced. A `ModelRun` represents a collection of
[processed clips](#processed_clips) that were generated in a single run using
the same processing method.

#### Ensuring Consistency and Comparability

By organizing [processed clips](#processed_clips) into `ModelRun` objects,
researchers can ensure that all clips within a run were analyzed in the same
exact manner. This guarantees consistency and comparability when comparing
results across different runs or when evaluating against other groups of
annotations.

#### Tracking Processing Method

The `ModelRun` object keeps track of the specific processing method that was
applied to generate the [processed clips](#processed_clips). This information is
crucial for reproducing and replicating the results, as well as for accurately
documenting the processing pipeline.

#### Comparative Analysis and Evaluation

`ModelRun` objects facilitate comparative analysis and evaluation of different
processing methods or runs. Researchers can easily compare the results and
performance of various models, algorithms, or parameter settings by examining
the [processed clips](#processed_clips) within each `ModelRun`.

## Evaluation

### Matches

In bioacoustic research, it is often necessary to compare and match sound events
between two different sources of [sound event](#sound_events_1) information. The
purpose of matching is to identify and pair [sound events](#sound_events_1) from
these sources based on some metric of similarity. The `Match` object represents
the result of this matching process, providing information about the matched
[sound events](#sound_events_1) and their **affinity score**.

#### Matching Process

The matching process involves comparing [sound events](#sound_events_1) from a
source and target. This comparison is typically based on a similarity metric
that quantifies the degree of similarity or relatedness between the sound
events. The matching algorithm pairs the closest sound events based on this
metric.

#### Match Object Structure

The `Match` object encapsulates the outcome of the matching process. It contains
references to the source and target [sound events](#sound_events_1) that were
matched, along with the affinity score that represents the level of similarity
between the matched pair. The affinity score can be used to evaluate the quality
or strength of the match.

#### Unmatched Sound Events

It is also important to consider the scenario where some sound events do not
have a matching counterpart in the other source. The `Match` object can handle
this situation by representing unmatched sound events with a null source or
target sound event. These unmatched sound events provide valuable information,
indicating that certain events were not successfully matched.

By utilizing the `Match` object, researchers can analyze and understand the
relationships between sound events from different sources, allowing for
comparative studies and insights in bioacoustic research.
