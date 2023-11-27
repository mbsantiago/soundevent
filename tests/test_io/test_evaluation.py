"""Test suite for saving and loading evaluation results."""

from pathlib import Path

from soundevent import data, io


def test_evaluation_is_recovered(
    evaluation: data.Evaluation,
    audio_dir: Path,
):
    """Test that the evaluation is recovered."""
    # Arrange
    path = audio_dir / "evaluation.json"

    # Act
    io.save(evaluation, path, audio_dir=audio_dir)
    recovered = io.load(path, audio_dir=audio_dir, type="evaluation")

    # Assert
    assert recovered == evaluation
