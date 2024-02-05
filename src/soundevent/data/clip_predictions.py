"""Processed Clips.

In the field of bioacoustics, it is common to process recording clips in order
to extract relevant information. This processing can involve the use of machine
learning models or non-machine learning pipelines specifically designed for
tasks such as sound event detection or automated acoustic feature extraction.
The `ProcessedClip` objects encapsulate the results of these processing steps.

## Types of Processing Results

The `ProcessedClip` objects capture the outcomes of the processing steps applied
to the recording clips. These outcomes can take different forms:

* Predicted Sound Events: The processing may involve the detection or
identification of sound events within the clip. The `ProcessedClip` object
stores the predicted sound events, providing information about their
characteristics, such as their temporal and frequency properties.

* Tags at Clip Level: The processing may also generate tags at the clip level,
providing high-level semantic information about the content of the clip. These
tags highlight specific aspects or categories of the acoustic content and can
aid in the organization and categorization of the clips.

* Features at Clip Level: The processing may extract acoustic features from the
clip, which can capture relevant information about the audio content. These
features can be numerical representations that describe properties such as
signal to noise ratio, spectral centroid, or other characteristics of the
acoustic content of the clip.

## Annotations and Additional Information

The predicted sound events within the `ProcessedClip` object can be further
enriched with tags and/or features associated with each predicted sound event.
These annotations and additional information provide more detailed insights
into the predicted events and aid in subsequent analysis and interpretation.
"""

from typing import Sequence
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.clips import Clip
from soundevent.data.features import Feature
from soundevent.data.predicted_tags import PredictedTag
from soundevent.data.sequence_predictions import SequencePrediction
from soundevent.data.sound_event_predictions import SoundEventPrediction

__all__ = ["ClipPrediction"]


class ClipPrediction(BaseModel):
    """Clip Prediction.

    Clip prediction encapsulate the outcomes of various processing steps
    applied to recording clips in bioacoustic research. These processing steps
    can include sound event detection, tag generation, and acoustic feature
    extraction.

    Attributes
    ----------
    uuid
        A unique identifier for the processed clip.
    clip
        The original clip that was processed, serving as the basis for the
        analysis.
    sound_events
        A list of predicted sound events detected within the clip. Each
        predicted sound event contains information about its characteristics,
        including temporal and frequency properties.
    tags
        A list of predicted tags generated at the clip level. These tags
        provide high-level semantic information about the clip's content,
        aiding in organization and categorization.
    features
        A list of acoustic features extracted from the clip. These features
        offer numerical representations describing properties such as
        signal-to-noise ratio, spectral centroid, or other acoustic
        characteristics. They enhance the understanding of the clip's acoustic
        content.
    """

    uuid: UUID = Field(default_factory=uuid4, repr=False)
    clip: Clip
    sound_events: Sequence[SoundEventPrediction] = Field(default_factory=list)
    sequences: Sequence[SequencePrediction] = Field(default_factory=list)
    tags: Sequence[PredictedTag] = Field(default_factory=list)
    features: Sequence[Feature] = Field(default_factory=list)

    def __hash__(self):
        """Hash function for the processed clip."""
        return hash(self.uuid)
