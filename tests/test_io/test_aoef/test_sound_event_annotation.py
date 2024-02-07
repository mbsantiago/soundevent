"""Test suite for AOEF sound event annotation adapter."""

from soundevent import data
from soundevent.io.aoef.sound_event_annotation import (
    SoundEventAnnotationAdapter,
    SoundEventAnnotationObject,
)


def test_sound_event_annotation_can_be_converted_to_aoef(
    sound_event_annotation: data.SoundEventAnnotation,
    sound_event_annotation_adapter: SoundEventAnnotationAdapter,
):
    obj = sound_event_annotation_adapter.to_aoef(sound_event_annotation)
    assert isinstance(obj, SoundEventAnnotationObject)


def test_sound_event_annotation_can_be_recovered(
    sound_event_annotation: data.SoundEventAnnotation,
    sound_event_annotation_adapter: SoundEventAnnotationAdapter,
):
    obj = sound_event_annotation_adapter.to_aoef(sound_event_annotation)
    recovered = sound_event_annotation_adapter.to_soundevent(obj)
    assert recovered == sound_event_annotation
