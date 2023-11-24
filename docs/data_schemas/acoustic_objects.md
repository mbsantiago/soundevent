# Sound Events

## Sound Events

The `soundevent` package is designed to focus on the analysis of sound events,
which play a crucial role in bioacoustic research. Sound events refer to
distinct and discernible sounds within a [recording](#recordings) that are of
particular interest for analysis. A recording can contain multiple sound events
or none at all, depending on the audio content.

### Identification and Localization

Sound events typically occur within a specific time range and occupy a limited
frequency space within a [recording](#recordings). There are various methods to
specify the location of these events, such as indicating the onset timestamp,
start and end times, or providing detailed information about the associated time
and frequency regions. These approaches enable precise localization and
description of sound events within the [recording](#recordings).

### Tags and Semantic Information

To provide meaningful context, sound events can be enriched with [tags](#tags),
which are labels attached to the events. These tags offer semantic information
about the sound events, including the species responsible for the sound, the
behavior exhibited by the sound emitter, or even the specific syllable within a
vocalization. Tags aid in organizing and categorizing sound events, enabling
more efficient analysis and interpretation.

### Features and Numerical Descriptors

In addition to [tags](#tags), sound events can be characterized by
[features](#features), which are numerical descriptors attached to the events.
These features provide quantitative information about the sound events, such as
duration, bandwidth, peak frequency, and other detailed measurements that can be
extracted using advanced techniques like deep learning models.
[Features](#features) offer valuable insights into the acoustic properties of
the sound events.

## Geometries

[Sound event](#sound_events_1) **geometry** plays a crucial role in locating and
describing sound events within a recording. Different geometry types offer
flexibility in representing the location of sound events, allowing for varying
levels of detail and precision. The `soundevent` package follows the
[GeoJSON](https://geojson.org/) specification for **geometry types** and
provides support for a range of geometry types.

### Units and Time Reference

All geometries in the `soundevent` package utilize **seconds** as the unit for
time and **hertz** as the unit for frequency. It is important to note that time
values are always **relative to the start of the recording**. By consistently
using these units, it becomes easier to develop functions and interact with
geometry objects based on convenient assumptions.

### Supported Geometry Types

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

## Sequences

Animal communication is a fascinating and intricate phenomenon, often consisting
of multiple vocalizations that form a cohesive message. In the `soundevent`
package, we introduce the concept of a `Sequence` object to represent these
complex vocalization patterns. A `Sequence` groups together multiple
[sound event](#sound-events) objects, allowing researchers to analyze and
understand the composition and dynamics of animal communication in a structured
manner.

### Flexible Modeling of Vocalization Patterns

The `Sequence` object is designed to provide flexibility to researchers,
allowing them to model a wide range of sequence types and behaviors. While the
[sound events](#sound_events_1) within a sequence should originate from the same
recording, no other restrictions are imposed, empowering researchers to tailor
the structure to their specific research needs.

### Sequence Description

Similar to individual [sound events](#sound_events_1), sequences can be enriched
with additional information using [tags](#tags), [features](#features), and
[notes](#notes). Researchers can attach categorical [tags](#tags) to describe
the type of sequence or the associated behavior, providing valuable insights
into the communication context. Additionally, numerical [features](#features)
can capture important characteristics of the sequence, such as overall duration,
inter-pulse interval, or any other relevant acoustic properties.

### Hierarchical Structure

Furthermore, recognizing the hierarchical nature of animal communication, the
`Sequence` object allows the inclusion of subsequences. Researchers can specify
a parent sequence, facilitating the representation of complex hierarchical
relationships within the vocalization structure.

By incorporating sequences into the analysis workflow, researchers gain a
flexible and expressive framework to explore and study the intricacies of animal
communication. The `Sequence` object, along with its associated tags, features,
and hierarchical capabilities, provides a powerful tool for understanding the
rich complexity of vocalization sequences.
