# Geometry Module

???+ info "Additional dependencies"

    To use the `soundevent.geometry` module you need to install some
    additional dependencies. Make sure you have them installed by running the
    following command:

    ```bash
    pip install "soundevent[geometry]"
    ```

    or, if you are using uv

    ```bash
    uv add "soundevent[geometry]"
    ```

The `soundevent.geometry` module provides a comprehensive set of tools for handling the spatial and temporal aspects of sound events. It is organised into several components:

*   [**Matching**](#matching): Tools for pairing sets of geometries.
*   [**Affinity**](#affinity_similarity): Functions to calculate similarity scores (e.g., IoU) between geometries.
*   [**Operations**](#geometric_operations): Core geometric manipulations (shifting, scaling, buffering) and queries.
*   [**Features**](#features): Extraction of geometric properties.
*   [**Conversion**](#conversion): Utilities to convert between `soundevent` geometries and `shapely` objects.
*   [**Visualisation**](#visualisation): Helpers for rendering geometries.

## Matching

::: soundevent.geometry.match

## Affinity & Similarity

::: soundevent.geometry.affinity

## Geometric Operations

::: soundevent.geometry.operations

## Features

::: soundevent.geometry.features

## Conversion

::: soundevent.geometry.conversion

## Visualisation

::: soundevent.geometry.html
