"""Prediction Set.

In bioacoustic research, it is common to apply the same processing pipeline to
a set of audio clips, such as all the clips in a dataset or a test set. To
maintain a reference to this group of processed clips and the specific
processing method used, the concept of a `ModelRun` is introduced. A `ModelRun`
represents a collection of processed clips that were generated in a single run
using the same processing method.

## Ensuring Consistency and Comparability

By organizing processed clips into `ModelRun` objects, researchers can ensure
that all clips within a run were analyzed in the same exact manner. This
guarantees consistency and comparability when comparing results across
different runs or when evaluating against other groups of annotations.

## Grouping Processed Clips

A `ModelRun` serves as a container for a set of processed clips that share a
common processing method. It provides a convenient way to organize and manage
the processed clips generated during a single run.

## Tracking Processing Method

The `ModelRun` object keeps track of the specific processing method that was
applied to generate the processed clips. This information is crucial for
reproducing and replicating the results, as well as for accurately documenting
the processing pipeline.

## Comparative Analysis and Evaluation

`ModelRun` objects facilitate comparative analysis and evaluation of different
processing methods or runs. Researchers can easily compare the results and
performance of various models, algorithms, or parameter settings by examining
the processed clips within each `ModelRun`.
"""

import datetime
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.clip_predictions import ClipPrediction

__all__ = ["PredictionSet"]


class PredictionSet(BaseModel):
    """ModelRun Class.

    The `ModelRun` class represents a collection of processed audio clips
    generated during a single run using the same processing method. In
    bioacoustic research, applying consistent processing pipelines to sets of
    audio clips is essential for maintaining comparability and ensuring the
    reliability of research results.

    Attributes
    ----------
    id
        The unique identifier of the model run, automatically generated upon
        creation.
    clips
        A list of `ProcessedClip` instances representing the audio clips
        processed during the run. These clips share a common processing history
        and are grouped within the same `ModelRun` for consistency and
        comparability.
    created_on
        The date and time when the `ModelRun` object was created. This
        timestamp provides information about the moment the processing run was
        initiated.
    """

    uuid: UUID = Field(default_factory=uuid4)
    clip_predictions: List[ClipPrediction] = Field(default_factory=list)
    created_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )
