"""Test suite for saving and loading evaluation sets."""

from pathlib import Path

from soundevent import data, io


def test_evaluation_set_is_recovered(
    evaluation_set: data.EvaluationSet,
    audio_dir: Path,
):
    """Test that the evaluation set is recovered."""
    # Arrange
    path = audio_dir / "evaluation_set.json"

    # Act
    io.save(evaluation_set, path, audio_dir=audio_dir)
    recovered = io.load(path, audio_dir=audio_dir)

    # Assert
    assert recovered == evaluation_set
