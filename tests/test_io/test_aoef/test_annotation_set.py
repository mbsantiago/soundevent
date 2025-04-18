"""Test Suite for AOEF Annotation Set Adapter."""

from pathlib import Path

from soundevent import data, io
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


def test_annotation_set_name_and_description_are_saved(
    tmp_path: Path,
    annotation_set: data.AnnotationSet,
):
    annotation_set = annotation_set.model_copy(
        update=dict(
            name="test_name",
            description="test description",
        )
    )

    # Save the annotation set to a file
    file_path = tmp_path / "test_aoef_annotation_set.json"
    io.save(annotation_set, file_path)

    # Load the annotation set from the file
    loaded_annotation_set = io.load(file_path)
    assert isinstance(loaded_annotation_set, data.AnnotationSet)
    assert loaded_annotation_set.name == "test_name"
    assert loaded_annotation_set.description == "test description"
