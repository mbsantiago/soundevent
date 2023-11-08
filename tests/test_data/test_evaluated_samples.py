"""Test suite for EvaluatedExamples validators."""

import pytest
from pydantic import ValidationError

from soundevent import data


def test_validation_error_if_clips_do_not_coincide(recording: data.Recording):
    """Test that we raise an error if the clips do not coincide."""
    with pytest.raises(ValidationError):
        data.EvaluatedExample(
            example=data.EvaluationExample(
                clip=data.Clip(
                    recording=recording,
                    start_time=0.0,
                    end_time=0.1,
                )
            ),
            prediction=data.ProcessedClip(
                clip=data.Clip(
                    recording=recording,
                    start_time=0.1,
                    end_time=0.2,
                ),
            ),
        )


def test_can_create_evaluated_example_with_the_same_clip(
    recording: data.Recording,
):
    """Test that we can create an evaluated example with the same clip."""
    clip = data.Clip(
        recording=recording,
        start_time=0.0,
        end_time=0.1,
    )
    data.EvaluatedExample(
        example=data.EvaluationExample(clip=clip),
        prediction=data.ProcessedClip(clip=clip),
    )


def test_raises_validation_error_if_repeated_target_match(
    clip: data.Clip,
    annotation: data.Annotation,
):
    """Test that we raise an error if the source is repeated."""
    with pytest.raises(ValidationError):
        data.EvaluatedExample(
            example=data.EvaluationExample(
                clip=clip,
                annotations=[annotation],
            ),
            prediction=data.ProcessedClip(clip=clip),
            matches=[
                data.Match(target=annotation),
                data.Match(target=annotation),
            ],
        )


def test_raises_validation_error_if_missing_target_annotation(
    clip: data.Clip,
    annotation: data.Annotation,
):
    """Test that we raise an error if the source is missing."""
    with pytest.raises(ValidationError):
        data.EvaluatedExample(
            example=data.EvaluationExample(
                clip=clip,
                annotations=[annotation],
            ),
            prediction=data.ProcessedClip(clip=clip),
            matches=[],
        )


def test_raises_validation_error_if_repeated_source_match(
    clip: data.Clip,
    predicted_sound_event: data.PredictedSoundEvent,
):
    """Test that we raise an error if the target is repeated."""
    with pytest.raises(ValidationError):
        data.EvaluatedExample(
            example=data.EvaluationExample(clip=clip),
            prediction=data.ProcessedClip(
                clip=clip,
                sound_events=[predicted_sound_event],
            ),
            matches=[
                data.Match(source=predicted_sound_event),
                data.Match(source=predicted_sound_event),
            ],
        )


def test_raises_validation_error_if_missing_source_annotation(
    clip: data.Clip,
    predicted_sound_event: data.PredictedSoundEvent,
):
    """Test that we raise an error if the target is missing."""
    with pytest.raises(ValidationError):
        data.EvaluatedExample(
            example=data.EvaluationExample(clip=clip),
            prediction=data.ProcessedClip(
                clip=clip,
                sound_events=[predicted_sound_event],
            ),
            matches=[],
        )


def test_raises_validation_error_if_unexpected_match_object(
    clip: data.Clip,
    predicted_sound_event: data.PredictedSoundEvent,
):
    """Test that we raise an error if the target is missing."""
    with pytest.raises(ValidationError):
        data.EvaluatedExample(
            example=data.EvaluationExample(clip=clip),
            prediction=data.ProcessedClip(clip=clip),
            matches=[
                data.Match(source=predicted_sound_event),
            ],
        )


def test_can_create_evaluated_example_with_matches(
    clip: data.Clip,
    annotation: data.Annotation,
    predicted_sound_event: data.PredictedSoundEvent,
):
    """Test that we can create an evaluated example with matches."""
    data.EvaluatedExample(
        example=data.EvaluationExample(
            clip=clip,
            annotations=[annotation],
        ),
        prediction=data.ProcessedClip(
            clip=clip,
            sound_events=[predicted_sound_event],
        ),
        matches=[
            data.Match(
                source=predicted_sound_event,
                target=annotation,
            ),
        ],
    )
