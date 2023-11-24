# Recordings and Clips

## Recordings

A recording represents a single audio file, typically an unmodified file
capturing the original audio as recorded by an audio recorder. Each recording is
uniquely identified by a **hash** or other unique identifier and is associated
with a file **path** pointing to the audio file itself. In addition to the audio
data, recordings often include relevant metadata that provides essential
information about the recording.

### Metadata

Recordings can be accompanied by metadata that offers valuable contextual
information. This metadata typically includes the **duration** of the recording,
**sample rate**, and the **number of audio channels**. These details help in
understanding the technical characteristics of the audio data and ensure
accurate processing and analysis.

### Date, Time, and Location Information

To provide temporal and spatial context, recordings can include **date** and
**time** information indicating when they were recorded. This allows for
organizing and comparing recordings based on the time of capture. **Latitude**
and **longitude** coordinates can also be associated with a recording,
indicating the geographical location where it was recorded. This information is
particularly useful in bioacoustic research and conservation efforts for
understanding species distributions and habitat characteristics.

### Attribution and Right Usage

### Extending Metadata

Metadata about a recording can be further enriched by attaching additional
[tags](#tags) or [features](#features). [Tags](#tags) provide categorical
information, such as the recording site, habitat type, or equipment used.
[Features](#features), on the other hand, offer numeric values that quantify
specific characteristics of the recording, such as temperature, wind speed, or
the height of the recording device.

### Textual Notes

Recordings can also have textual [notes](#notes) attached to them, allowing
users to add descriptive information, comments, or discussion points. These
[notes](#notes) provide additional context, insights, or relevant details that
contribute to a deeper understanding of the recording.

The combination of metadata, [tags](#tags), [features](#features), and textual
[notes](#notes) associated with recordings facilitates effective organization,
searchability, and analysis of audio data in bioacoustic research and related
fields.

## Clips

A clip represents a contiguous fragment of a [recording](#recording), defined by
its **start** and **end** times. While [recordings](#recordings) serve as the
base source of information, clips are the fundamental unit of work in many
[analysis](#automated_analysis) and [annotation tasks](#annotations). When
annotating audio or running machine learning models, the focus is often on
working with clips rather than the entire recording.

### Benefits of Using Clips

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

### Tags and Features

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

## Datasets

Datasets play a important role in the organization and management of audio
[recordings](#recordings) in the field of audio analysis and research. They
serve as logical collections of audio [recordings](#recordings), consolidating
recordings that are associated with a specific context, such as a deployment or
field study. While datasets typically consist of recordings captured by the same
group of individuals using similar equipment and following a predefined
protocol, it is important to note that adherence to these criteria is not
mandatory.

### Naming and Description

Each dataset should be given a meaningful **name** and accompanied by a
**descriptive summary**. The name of the dataset should succinctly convey the
common theme or purpose of the recordings it contains. This enables users to
easily identify and differentiate between multiple datasets. Additionally, the
description provides valuable contextual information about the dataset,
including details about its origin, context, and relevance, facilitating a
deeper understanding of its content.

### Advantages of Datasets

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

### Utilizing Datasets

By leveraging datasets, researchers can effectively structure their audio data,
ensuring ease of access, maintainability, and reproducibility of their
experiments and analyses. Datasets provide a systematic and organized approach
to managing audio [recordings](#recordings), facilitating efficient research
workflows and promoting robust scientific practices.
