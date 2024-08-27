# soundevent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/soundevent.svg)](https://badge.fury.io/py/soundevent)
![tests](https://github.com/mbsantiago/soundevent/actions/workflows/test.yml/badge.svg)
[![docs](https://github.com/mbsantiago/soundevent/actions/workflows/docs.yml/badge.svg)](https://mbsantiago.github.io/soundevent/)
![Python 3.9 +](https://img.shields.io/badge/python->=_3.9-blue.svg)
![Static Badge](https://img.shields.io/badge/formatting-black-black)
[![codecov](https://codecov.io/gh/mbsantiago/soundevent/branch/main/graph/badge.svg?token=42kVE87avA)](https://codecov.io/gh/mbsantiago/soundevent)

> **Warning** This package is under active development, use with caution.

`soundevent` is an open-source Python package that aims to support the
computational biocoustic community in developing well-tested, coherent, and
standardized software tools for bioacoustic analysis. The main goal of the
package is to provide a flexible yet consistent definition of what a sound event
is in a computational sense, along with a set of tools to easily work with this
definition. The package comprises three key components:

## Main features

### 1. Data Schemas for Bioacoustic Analysis

The `soundevent` package introduces several
[data schemas](https://mbsantiago.github.io/soundevent/data_schemas/) designed
to conceptualize and standardize recurring objects in bioacoustic analysis.
These data schemas establish relationships between various concepts and define
the attributes each object possesses. They provide flexibility to cover a broad
spectrum of use cases in bioacoustic analysis while incorporating data
validation mechanisms to ensure stored information is both valid and meaningful.
Notably, the package defines schemas related to sound events, including user
annotations and model predictions.

### 2. Serialization, Storage, and Reading Functions

To promote standardized data formats for storing annotated datasets and other
information about sounds in recordings, the `soundevent` package provides
[several functions](https://mbsantiago.github.io/soundevent/generated/gallery/1_saving_and_loading/)
for serialization, storage, and reading of the different data classes offered.
These functions enable easy sharing of information about common objects in
bioacoustic research. By employing a consistent data format, researchers can
exchange data more efficiently and collaborate seamlessly.

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
[documentation](https://mbsantiago.github.io/soundevent/).

## Example Usage

To see practical examples of how to use soundevent, you can explore the
collection of examples provided in the
[documentation's gallery](https://mbsantiago.github.io/soundevent/generated/gallery/).

## Contributing

We welcome contributions from the community to make `soundevent` even better. If
you would like to contribute, please refer to the
[contribution guidelines](CONTRIBUTING.md).

## License

`soundevent` is released under the MIT License.
