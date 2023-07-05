# soundevent

> **Warning**
> This package is under active development use with caution. 
> However, most of the data definitions are not expected to change. 
> Will be adding data loading/exporting and prediction evaluation functions soon. 

`soundevent` is an open-source Python package that aims to support the
computational biocoustic community in developing well-tested, coherent, and
standardized software tools for bioacoustic analysis. The main goal of the
package is to provide a flexible yet consistent definition of what a sound event
is in a computational sense, along with a set of tools to easily work with this
definition. The package comprises three key components:

## Main features

### 1. Data Classes for Bioacoustic Analysis

The `soundevent` package defines several data classes that conceptualize and
standardize different recurrent objects in bioacoustic analysis. These data
classes establish the relationships between various concepts and specify the
attributes each object possesses. They are designed to be flexible enough to
cover a wide range of use cases in bioacoustic analysis. The package also
includes data validation mechanisms to ensure that the information stored is
valid and meaningful. Specifically, it defines objects related to sound events,
such as user annotations and model predictions.

### 2. Serialization, Storage, and Reading Functions

To promote standardized data formats for storing annotated datasets and other
information about sounds in recordings, the `soundevent` package provides
several functions for serialization, storage, and reading of the different data
classes offered. These functions enable easy sharing of information about common
objects in bioacoustic research. By employing a consistent data format,
researchers can exchange data more efficiently and collaborate seamlessly.

### 3. Handling Functions for Sound Events

The `soundevent` package also includes a variety of functions that facilitate
the handling of sound event objects. These functions serve multiple purposes,
such as matching sound events for model prediction evaluation, transforming
sound events, and managing metadata and labels. By offering a comprehensive set
of handling functions, the package aims to streamline the analysis workflow for
bioacoustic researchers, providing them with powerful tools to manipulate and
extract insights from their data.

## Installation

You can install `soundevent` using pip:

```{shell}
pip install soundevent
```

## Documentation

For detailed information on how to use the package, please refer to the
[documentation](https://github.com/mbsantiago/soundevent/settings/pages).

## Example Usage

Here's a brief example demonstrating the usage of `soundevent` package:

``` py
import soundevent

dataset = soundevent.load_dataset("example_dataset.json", audio_dir="audio")
print(f"Dataset {dataset.name} has {len(dataset.recordings)} Recordings")

recording = dataset.recordings[0]
print(f"Recording {recording.id}:  duration={recording.duration}, samplerate={recording.samplerate}")

wav = soundevent.load_recording_audio(recording)

```

## Contributing

We welcome contributions from the community to make `soundevent` even better. If
you would like to contribute, please refer to the [contribution guidelines](CONTRIBUTING.md).

## License

`soundevent` is released under the MIT License.
