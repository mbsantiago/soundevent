"""Test suite for saving and loading annotation sets."""

from pathlib import Path

from soundevent import data, io


def test_annotation_set_is_recovered(
    annotation_set: data.AnnotationSet,
    audio_dir: Path,
):
    """Test that the annotation set is recovered."""
    # Arrange
    path = audio_dir / "annotation_set.json"

    # Act
    io.save(annotation_set, path, audio_dir=audio_dir)
    recovered = io.load(path, audio_dir=audio_dir, type="annotation_set")

    # Assert
    assert annotation_set == recovered
