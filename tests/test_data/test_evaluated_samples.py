"""Test suite for EvaluatedExamples validators."""

import pytest
from pydantic import ValidationError

from soundevent import data


def test_validation_error_if_clips_do_not_coincide(recording: data.Recording):
    """Test that we raise an error if the clips do not coincide."""
    with pytest.raises(ValidationError):
        data.ClipEvaluation(
            annotations=data.ClipAnnotation(
                clip=data.Clip(
                    recording=recording,
                    start_time=0.0,
                    end_time=0.1,
                )
            ),
            predictions=data.ClipPrediction(
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
    data.ClipEvaluation(
        annotations=data.ClipAnnotation(clip=clip),
        predictions=data.ClipPrediction(clip=clip),
    )


def test_raises_validation_error_if_repeated_target_match(
    clip: data.Clip,
    sound_event_annotation: data.SoundEventAnnotation,
):
    """Test that we raise an error if the source is repeated."""
    with pytest.raises(ValidationError):
        data.ClipEvaluation(
            annotations=data.ClipAnnotation(
                clip=clip,
                sound_events=[sound_event_annotation],
            ),
            predictions=data.ClipPrediction(clip=clip),
            matches=[
                data.Match(target=sound_event_annotation),
                data.Match(target=sound_event_annotation),
            ],
        )


def test_raises_validation_error_if_missing_target_annotation(
    clip: data.Clip,
    sound_event_annotation: data.SoundEventAnnotation,
):
    """Test that we raise an error if the source is missing."""
    with pytest.raises(ValidationError):
        data.ClipEvaluation(
            annotations=data.ClipAnnotation(
                clip=clip,
                sound_events=[sound_event_annotation],
            ),
            predictions=data.ClipPrediction(clip=clip),
            matches=[],
        )


def test_raises_validation_error_if_repeated_source_match(
    clip: data.Clip,
    sound_event_prediction: data.SoundEventPrediction,
):
    """Test that we raise an error if the target is repeated."""
    with pytest.raises(ValidationError):
        data.ClipEvaluation(
            annotations=data.ClipAnnotation(clip=clip),
            predictions=data.ClipPrediction(
                clip=clip,
                sound_events=[sound_event_prediction],
            ),
            matches=[
                data.Match(source=sound_event_prediction),
                data.Match(source=sound_event_prediction),
            ],
        )


def test_raises_validation_error_if_missing_source_annotation(
    clip: data.Clip,
    sound_event_prediction: data.SoundEventPrediction,
):
    """Test that we raise an error if the target is missing."""
    with pytest.raises(ValidationError):
        data.ClipEvaluation(
            annotations=data.ClipAnnotation(clip=clip),
            predictions=data.ClipPrediction(
                clip=clip,
                sound_events=[sound_event_prediction],
            ),
            matches=[],
        )


def test_raises_validation_error_if_unexpected_match_object(
    clip: data.Clip,
    sound_event_prediction: data.SoundEventPrediction,
):
    """Test that we raise an error if the target is missing."""
    with pytest.raises(ValidationError):
        data.ClipEvaluation(
            annotations=data.ClipAnnotation(clip=clip),
            predictions=data.ClipPrediction(clip=clip),
            matches=[
                data.Match(source=sound_event_prediction),
            ],
        )


def test_can_create_evaluated_example_with_matches(
    clip: data.Clip,
    sound_event_annotation: data.SoundEventAnnotation,
    sound_event_prediction: data.SoundEventPrediction,
):
    """Test that we can create an evaluated example with matches."""
    data.ClipEvaluation(
        annotations=data.ClipAnnotation(
            clip=clip,
            sound_events=[sound_event_annotation],
        ),
        predictions=data.ClipPrediction(
            clip=clip,
            sound_events=[sound_event_prediction],
        ),
        matches=[
            data.Match(
                source=sound_event_prediction,
                target=sound_event_annotation,
            ),
        ],
    )
