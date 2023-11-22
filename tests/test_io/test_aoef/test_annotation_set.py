"""Test Suite for AOEF Annotation Set Adapter."""

from soundevent import data
from soundevent.io.aoef.annotation_set import (
    AnnotationSetAdapter,
    AnnotationSetObject,
)


def test_annotation_set_can_be_converted_to_aoef(
    annotation_set: data.AnnotationSet,
    annotation_set_adapter: AnnotationSetAdapter,
):
    obj = annotation_set_adapter.to_aoef(annotation_set)
    assert isinstance(obj, AnnotationSetObject)


def test_annotation_set_can_be_recovered(
    annotation_set: data.AnnotationSet,
    annotation_set_adapter: AnnotationSetAdapter,
):
    obj = annotation_set_adapter.to_aoef(annotation_set)
    recovered = annotation_set_adapter.to_soundevent(obj)
    assert annotation_set == recovered
