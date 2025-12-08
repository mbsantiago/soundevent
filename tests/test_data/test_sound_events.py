"""Tests for the SoundEvent data model."""

import pytest
from pydantic import ValidationError

from soundevent.data.geometries import BoundingBox
from soundevent.data.recordings import Recording
from soundevent.data.sound_events import SoundEvent


def test_sound_event_geometry_mandatory(recording: Recording):
    # GIVEN a SoundEvent definition
    # WHEN instantiated without a geometry
    # THEN it should raise a ValidationError
    with pytest.raises(ValidationError):
        SoundEvent(
            recording=recording,
            geometry=None,  # type: ignore
        )

    # Attempting to create a SoundEvent without providing geometry
    with pytest.raises(ValidationError):
        SoundEvent(recording=recording)  # type: ignore


def test_sound_event_geometry_valid(
    recording: Recording,
    bounding_box: BoundingBox,
):
    # GIVEN a SoundEvent definition
    # WHEN instantiated with a valid geometry
    # THEN it should be created successfully
    sound_event = SoundEvent(
        recording=recording,
        geometry=bounding_box,
    )
    assert sound_event.geometry == bounding_box
    assert sound_event.recording == recording
