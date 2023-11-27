"""Test suite for AOEF Sequence Annotation Adapter."""

from soundevent import data
from soundevent.io.aoef.sequence_annotation import (
    SequenceAnnotationAdapter,
    SequenceAnnotationObject,
)


def test_sequence_annotation_can_be_converted_to_aoef(
    sequence_annotation: data.SequenceAnnotation,
    sequence_annotation_adapter: SequenceAnnotationAdapter,
):
    """Test that a sequence annotation can be converted to AOEF."""
    aoef = sequence_annotation_adapter.to_aoef(sequence_annotation)
    assert isinstance(aoef, SequenceAnnotationObject)


def test_sequence_annotation_is_recovered(
    sequence_annotation: data.SequenceAnnotation,
    sequence_annotation_adapter: SequenceAnnotationAdapter,
):
    """Test that a sequence annotation can be recovered from AOEF."""
    aoef = sequence_annotation_adapter.to_aoef(sequence_annotation)
    recovered = sequence_annotation_adapter.to_soundevent(aoef)
    assert recovered == sequence_annotation
