"""Test suite for AOEF Clip Annotation Adapter."""

from soundevent import data
from soundevent.io.aoef.clip_annotations import (
    ClipAnnotationsAdapter,
    ClipAnnotationsObject,
)


def test_clip_annotations_can_be_converted_to_aoef(
    clip_annotations: data.ClipAnnotation,
    clip_annotations_adapter: ClipAnnotationsAdapter,
):
    obj = clip_annotations_adapter.to_aoef(clip_annotations)
    assert isinstance(obj, ClipAnnotationsObject)


def test_clip_annotations_are_recovered(
    clip_annotations: data.ClipAnnotation,
    clip_annotations_adapter: ClipAnnotationsAdapter,
):
    obj = clip_annotations_adapter.to_aoef(clip_annotations)
    recovered = clip_annotations_adapter.to_soundevent(obj)
    assert clip_annotations == recovered
