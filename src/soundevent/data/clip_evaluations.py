"""Evaluated Example Module.

The `EvaluatedExample` class within the `soundevent.data` package represents a
specific example that has been evaluated by a machine learning model in the
context of bioacoustic analysis. This class contains detailed information about
the evaluation process, including the original `EvaluationExample`, the model's
predictions (`ProcessedClip`), matches between predicted and ground truth
annotations (`Match` instances), and computed evaluation metrics.
"""

from typing import Optional, Sequence
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from soundevent.data.clip_annotations import ClipAnnotation
from soundevent.data.clip_predictions import ClipPrediction
from soundevent.data.features import Feature
from soundevent.data.matches import Match

__all__ = ["ClipEvaluation"]


class ClipEvaluation(BaseModel):
    """Evaluated example model.

    Attributes
    ----------
    annotations
        An instance of the `ClipAnnotations` class representing the original
        annotations for the evaluated example. This object contains the audio
        clip, ground truth annotations, and other relevant information
        necessary for evaluation.
    prediction
        An instance of the `ProcessedClip` class representing the model's
        predictions for the given example. This processed clip encapsulates the
        model's annotations and predictions, providing a standardized format
        for comparison and analysis.
    matches
        A list of `Match` instances representing the matches between the
        model's predictions and the ground truth annotations. Each `Match`
        object contains information about the predicted and actual annotations
        that align, allowing for detailed analysis of correct predictions and
        potential errors.
    metrics
        A list of `Feature` instances representing computed evaluation metrics
        for the evaluated example. These metrics quantify the model's
        performance on this specific instance, offering numerical insights into
        accuracy, precision, recall, and other relevant evaluation criteria.
    score
        A float representing the overall score for the evaluated example. This
        score is usually some combination of the evaluation metrics, providing
        a single value that can be used to compare different models and
        evaluation examples. Can be used to rank predictions based on their
        overall score
    """

    uuid: UUID = Field(default_factory=uuid4, repr=False)
    annotations: ClipAnnotation
    predictions: ClipPrediction
    matches: Sequence[Match] = Field(default_factory=list)
    metrics: Sequence[Feature] = Field(default_factory=list)
    score: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    @model_validator(mode="after")  # type: ignore
    def _check_clips_match(self):
        """Check that the example and prediction clips are the same."""
        example = self.annotations
        prediction = self.predictions
        if example.clip.uuid != prediction.clip.uuid:
            raise ValueError("The example and prediction clips do not match.")
        return self

    @model_validator(mode="after")  # type: ignore
    def _check_matches(self):
        """Check that the matches are valid.

        Matches are considered valid if they satisfy the following criteria:

        1. Every example sound event appears in exactly one match.
        2. Every predicted sound event appears in exactly one match.

        Notes
        -----
        A match is only considered valid if the source and target sound events
        are not both null. This means that the match must contain at least one
        sound event. This validation is handled by the Match model.
        """
        annotation_sound_events = {
            annotation.uuid for annotation in self.annotations.sound_events
        }

        predicted_sound_events = {
            prediction.uuid for prediction in self.predictions.sound_events
        }

        match_targets = [
            match.target.uuid
            for match in self.matches
            if match.target is not None
        ]

        match_targets_set = set(match_targets)

        match_sources = [
            match.source.uuid
            for match in self.matches
            if match.source is not None
        ]

        match_sources_set = set(match_sources)

        if len(match_targets) != len(match_targets_set):
            raise ValueError("Multiple matches for the same target.")

        if len(match_sources) != len(match_sources_set):
            raise ValueError("Multiple matches for the same source.")

        if match_targets_set != annotation_sound_events:
            raise ValueError("Not all example sound events were matched.")

        if match_sources_set != predicted_sound_events:
            raise ValueError("Not all predicted sound events were matched.")

        return self
