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
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent.data.clips import Clip
from soundevent.data.features import Feature
from soundevent.data.predicted_sound_events import PredictedSoundEvent
from soundevent.data.predicted_tags import PredictedTag


class ProcessedClip(BaseModel):
    """Processed clip."""

    uuid: UUID = Field(default_factory=uuid4, repr=False)
    """Unique identifier for the processed clip."""

    clip: Clip
    """The clip that was processed."""

    sound_events: List[PredictedSoundEvent] = Field(default_factory=list)
    """List of predicted sound events."""

    tags: List[PredictedTag] = Field(default_factory=list)
    """List of predicted tags at the clip level."""

    features: List[Feature] = Field(default_factory=list)
    """List of features associated with the clip."""

    def __hash__(self):
        """Hash function for the processed clip."""
        return hash(self.uuid)
