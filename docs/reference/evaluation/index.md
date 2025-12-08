# Evaluation

The `soundevent.evaluation` module provides a comprehensive suite of tools for evaluating sound event analysis systems.
It covers various tasks ranging from simple clip-level classification to detailed sound event detection.

???+ info "Additional dependencies"

    To use the `soundevent.evaluation` module you need to install some
    additional dependencies. Make sure you have them installed by running the
    following command:

    ```bash
    pip install soundevent[evaluation]
    ```

## Evaluation Tasks

The module supports several standard evaluation tasks.
Each task corresponds to a specific way of framing the bioacoustic problem and requires different inputs and metrics.

- [**Sound Event Detection (SED)**](sound_event_detection.md): Evaluating systems that detect and classify sound events corresponding to a Region of Interest in the time-frequency domain.
- [**Clip Classification**](clip_classification.md): Evaluating systems that assign a single label to an entire audio clip.
- [**Clip Multilabel Classification**](clip_multilabel_classification.md): Evaluating systems that can assign multiple labels to an audio clip (e.g., multiple species present).
- [**Sound Event Classification**](sound_event_classification.md): Evaluating systems that classify pre-segmented sound events.

## Core Components

The evaluation module is built upon several core components that handle matching, scoring, and encoding.

### Matching

Algorithms for matching predictions to ground truth annotations.

::: soundevent.evaluation.match

### Affinity

Functions to compute the similarity (affinity) between geometries (e.g., IoU, temporal distance).

::: soundevent.evaluation.affinity

### Encoding

Utilities for encoding tags and predictions into numerical formats for metric computation.

::: soundevent.evaluation.encoding
