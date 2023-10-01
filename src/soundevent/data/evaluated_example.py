"""Evaluated Example Module.

The `EvaluatedExample` class within the `soundevent.data` package represents a
specific example that has been evaluated by a machine learning model in the
context of bioacoustic analysis. This class contains detailed information about
the evaluation process, including the original `EvaluationExample`, the model's
predictions (`ProcessedClip`), matches between predicted and ground truth
annotations (`Match` instances), and computed evaluation metrics.
"""
from typing import List

from pydantic import BaseModel, Field, model_validator

from soundevent.data.evaluation_example import EvaluationExample
from soundevent.data.features import Feature
from soundevent.data.matches import Match
from soundevent.data.processed_clip import ProcessedClip


class EvaluatedExample(BaseModel):
    """Evaluated example model.

    Attributes
    ----------
    example : EvaluationExample
        An instance of the `EvaluationExample` class representing the original
        example used for evaluation. This object contains the audio clip,
        ground truth annotations, and other relevant information necessary for
        evaluation.
    prediction : ProcessedClip
        An instance of the `ProcessedClip` class representing the model's
        predictions for the given example. This processed clip encapsulates the
        model's annotations and predictions, providing a standardized format
        for comparison and analysis.
    matches : List[Match]
        A list of `Match` instances representing the matches between the
        model's predictions and the ground truth annotations. Each `Match`
        object contains information about the predicted and actual annotations
        that align, allowing for detailed analysis of correct predictions and
        potential errors.
    metrics : List[Feature]
        A list of `Feature` instances representing computed evaluation metrics
        for the evaluated example. These metrics quantify the model's
        performance on this specific instance, offering numerical insights into
        accuracy, precision, recall, and other relevant evaluation criteria.

    """

    example: EvaluationExample

    prediction: ProcessedClip

    matches: List[Match] = Field(default_factory=list)

    metrics: List[Feature] = Field(default_factory=list)

    @model_validator(mode="after")  # type: ignore
    def _check_clips_match(self):
        """Check that the example and prediction clips are the same."""
        example = self.example
        prediction = self.prediction
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
        target_sound_events = {
            annotation.sound_event.uuid
            for annotation in self.example.annotations
        }

        predicted_sound_events = {
            prediction.sound_event.uuid
            for prediction in self.prediction.sound_events
        }

        match_targets = [
            match.target for match in self.matches if match.target is not None
        ]

        match_targets_set = set(match_targets)

        match_sources = [
            match.source for match in self.matches if match.source is not None
        ]

        match_sources_set = set(match_sources)

        if len(match_targets) != len(match_targets_set):
            raise ValueError("Multiple matches for the same target.")

        if len(match_sources) != len(match_sources_set):
            raise ValueError("Multiple matches for the same source.")

        if match_targets_set != target_sound_events:
            raise ValueError("Not all example sound events were matched.")

        if match_sources_set != predicted_sound_events:
            raise ValueError("Not all predicted sound events were matched.")

        return self
