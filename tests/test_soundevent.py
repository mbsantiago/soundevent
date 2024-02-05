"""Unit tests for soundevent."""

import soundevent


def test_has_version_number():
    """Test that soundevent has a version number."""
    assert hasattr(soundevent, "__version__")


def failing_test():
    raise Exception("This test is supposed to fail.")
